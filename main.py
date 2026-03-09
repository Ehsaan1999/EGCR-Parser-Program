import os
from dotenv import load_dotenv
import google.genai as genai
from utils.PageNumberDetector import PageNumberDetector
from utils.first_page import find_transcript_start_page
from llm.data_extractor import LLMExtractor
from prompts import post_transcript_prompt, pre_transcript_prompt, notice_prompt, rb_prompt, other_notice_prompt, post_transcript_prompt_florida, title_page_prompt, exhibit_prompt
from notice.document_reader import DocumentReader
from rb.rb import fetch_and_process_sheets
from utils.index_helpers import validate_examination_headings,validate_exhibits_headings
from utils.env_loader import resource_path
env_path = resource_path(".env")
load_dotenv(env_path)

def process_documents(TEXT_FOLDER, FILENAME, NOTICE_FILENAME, jobNo, hasMatchingNotice, progress_callback=None):
    def emit_stage(stage: str):
        if progress_callback:
            progress_callback(stage=stage)
    emit_stage("Starting Document Processing...")
    LAST_N_PAGES = int(os.getenv("LAST_N_PAGES", "4"))
    FULL_PATH = os.path.join(TEXT_FOLDER, FILENAME)
    # --------------------------------------------------    
    # 1. Run Page Number Detector
    # --------------------------------------------------
    detector = PageNumberDetector(
        text_folder=TEXT_FOLDER,
        min_gap_lines=int(os.getenv("MIN_GAP_LINES", 25)),
        enforce_left_pad_format=True
    )
    document_data = detector.run(filename_filter=FILENAME)
    page_map = document_data.get("page_map", {})
    
    print(f"Page Map detected: {len(page_map)} pages found.")
    if len(page_map) < 4:
        raise Exception("Could not parse file correctly/file too short.")
    if not page_map:
        raise Exception("Could not parse file correctly/file too short.")

    # --------------------------------------------------
    # 2. Read File (robust encoding handling)
    # --------------------------------------------------
    if not os.path.exists(FULL_PATH):
        raise FileNotFoundError(f"File not found: {FULL_PATH}")

    encodings_to_try = ["utf-8", "cp1252", "latin-1"]
    raw_text = None

    for encoding in encodings_to_try:
        try:
            with open(FULL_PATH, "r", encoding=encoding) as f:
                raw_text = f.read()
            print(f"Successfully read file using encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("⚠️ Forcing read with replacement characters.")
        with open(FULL_PATH, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

    # --------------------------------------------------
    # CRITICAL FIX:
    # Remove FORM FEED characters without adding lines
    # --------------------------------------------------
    raw_text = raw_text.replace("\x0c", " ")

    # Now split into lines safely
    all_lines = raw_text.splitlines()

    # --------------------------------------------------
    # 2.5 PRE-PROCESSING GUARDRAIL (Scout Check)
    # --------------------------------------------------
    # We scan the first ~50 lines for keywords to determine job type 
    # BEFORE finding the start page.

    preview_text = "\n".join(all_lines[:50]).lower()
    is_depo_euo_cona = any(kw in preview_text for kw in [
        "deposition", 
        "examination under oath", 
        "certificate of non-appearance",
        "e.u.o."
    ])

    if is_depo_euo_cona:
        print("✅ Scout Check: Depo/EUO/CONA detected. 'Proceedings' keyword will be ignored for start detection.")

    # --------------------------------------------------
    # 3. Find transcript start page (pages 3+)
    # --------------------------------------------------

    emit_stage("Locating Transcript...")
    # PASS THE SCOUT FLAG HERE
    found_page, matched_text = find_transcript_start_page(all_lines, page_map, is_depo_euo_cona=is_depo_euo_cona)
    if not found_page:
        raise Exception("No matching transcript start page found (Required page 3+ start).")
    print(f"✅ Transcript START detected on Page: {found_page}")
    print(f"   (Matched Line Content: '{matched_text}')")

    # --------------------------------------------------
    # 4. Build HEADER text (start → end of first transcript page)
    # --------------------------------------------------
    if found_page not in page_map:
        raise Exception(f"Page {found_page} missing from page map indexing.")
    _, first_transcript_end = page_map[found_page]
    header_text = "\n".join(all_lines[:first_transcript_end])
    print("\n--- Header Text ---")
    print(f"Lines 1 → {first_transcript_end}")

    # --------------------------------------------------
    # 5. Build TRAILER text (last N pages)
    # --------------------------------------------------
    sorted_pages = sorted(page_map.keys())
    last_pages = sorted_pages[-LAST_N_PAGES:]
    trailer_start = min(page_map[p][0] for p in last_pages)
    trailer_end = max(page_map[p][1] for p in last_pages)
    # Convert 1-based → 0-based slicing
    trailer_text = "\n".join(all_lines[trailer_start - 1 : trailer_end])
    print("\n--- Trailer Text ---")
    print(f"Pages: {last_pages}")
    print(f"Lines {trailer_start} → {trailer_end}")

    # --------------------------------------------------
    # 6. Send to LLM
    # --------------------------------------------------
    emit_stage("Extracting Pre-Transcript Data...")
    extractor = LLMExtractor()
    print("\n--- Pre Transcript Extraction Result ---")
    pre_json = extractor.extract_pre_transcript(
        prompt=pre_transcript_prompt.prompt,
        text=header_text
    )
    print(pre_json)

    emit_stage("Extracting Post-Transcript Data...")
    print("\n--- Post Transcript Extraction Result ---")
    court_heading = pre_json.get("court_heading", "")
    post_json = {}
    isFlorida = False
    
    if "florida" in court_heading.lower():
        isFlorida = True
        post_json = extractor.extract_post_transcript_florida(
            prompt=post_transcript_prompt_florida.prompt,
            text=trailer_text
        )
    else:
        post_json = extractor.extract_post_transcript(
            prompt=post_transcript_prompt.prompt,
            text=trailer_text
        )
    print(post_json)

    combined_data = {}

    if isinstance(pre_json, dict):
        combined_data.update(pre_json)
    if isinstance(post_json, dict):
        combined_data.update(post_json)

    ######################################################################
    # Dynamic Notary Public Check (Florida Only)
    ######################################################################

    combined_data["notary_public_check"] = False

    if isFlorida and page_map:
        try:
            # Get all keys and find the minimum numerical value
            all_keys = list(page_map.keys())
            # Convert to int for sorting to find the true first page
            numeric_keys = [int(k) for k in all_keys]
            smallest_val = min(numeric_keys)
            
            # Try to fetch using the original key type from the map
            # This handles if keys are strings "1" or integers 1
            first_page_key = next(k for k in all_keys if int(k) == smallest_val)
            first_page_indices = page_map[first_page_key]
            
            # all_lines is 0-indexed, so we subtract 1 from the start index
            start_idx = first_page_indices[0] - 1
            end_idx = first_page_indices[1]
            first_page_text = "\n".join(all_lines[start_idx : end_idx]).lower()

            if "notary public" in first_page_text:
                combined_data["notary_public_check"] = True
                print(f"✅ Notary Public found on physical first page (Page {first_page_key})")
            else:
                # Debug print to see what was actually read if it fails
                print(f"ℹ️ Notary not found in text of Page {first_page_key}")
                
        except (ValueError, KeyError, IndexError, StopIteration) as e:
            print(f"⚠️ Could not check first page for Notary: {e}")
    
    raw_keys = os.getenv("KEYS_FOR_NOTICE_COMPARISON", "")

    # --------------------------------------------------
    # Index to Appearances & Exhibits (SAFE HANDLING)
    # --------------------------------------------------

    # Ensure these are always lists, even if LLM returned None/null
    examinations_list = combined_data.get("examinations_proceedings_page_numbers") or []
    exhibits_list = combined_data.get("exhibits_page_numbers") or []

    # Pass the lists of dictionaries directly to the functions
    failed_exam_pages = validate_examination_headings(
        examinations_list=examinations_list,
        page_map=page_map,
        all_lines=all_lines
    )

    failed_exhibit_pages = validate_exhibits_headings(
        exhibits_list=exhibits_list,
        page_map=page_map,
        all_lines=all_lines
    )

    # Store the list of strings (page numbers) that failed validation
    combined_data["index_to_examinations_proceedings"] = failed_exam_pages
    combined_data["index_to_exhibits"] = failed_exhibit_pages

    # --------------------------------------------------
    # 6.5. Exhibit Folder Detection: Folder Word -> Witness Name
    # --------------------------------------------------

    # Get a list of file names in the exhibits subfolder
    # Get the exhibit page numbers list (specifically the names) from the combined data
    # Send both to prompt/schema
    # Get the result back as a list of exhibit names that have a corresponding folder, and Exact match/Partial match/No Match/Missing for each


    # Step 1
    all_exhibit_filenames = []

    # Parse witness first/last name from FILENAME (e.g. 119698.flood.mark.01072025.txt)
    _fname_parts = FILENAME.split(".")
    _witness_last  = _fname_parts[1].lower() if len(_fname_parts) >= 3 else ""
    _witness_first = _fname_parts[2].lower() if len(_fname_parts) >= 3 else ""

    if os.path.exists(TEXT_FOLDER):
        for entry in os.listdir(TEXT_FOLDER):
            full_path = os.path.join(TEXT_FOLDER, entry)

            # 1. Only look at directories containing the word 'exhibit' AND the witness's first and last name
            if os.path.isdir(full_path) and "exhibit" in entry.lower() and _witness_last in entry.lower() and _witness_first in entry.lower():
                # List all items in the current 'exhibit' folder
                files_in_folder = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
                
                # Extend the master list so it contains files from all matching folders
                all_exhibit_filenames.extend(files_in_folder)
    print(f"✅ Found {all_exhibit_filenames} exhibit files across all 'exhibit' folders.")

    #STep 2
    # 1. Retrieve the list of PageReference objects
    exh_items = combined_data.get("exhibits_page_numbers") or []
    # 2. Extract just the "name" field from each object into a list of strings
    exhibit_names_list = [exh.get("name", "") for exh in exh_items]
    print(f"✅ Extracted exhibit names from combined data: {exhibit_names_list}")

    #Step 3
    exhibit_result = extractor.extract_exhibit_comparison(
        prompt=exhibit_prompt.exhibit_comparison_prompt,
        exhibit_filenames=all_exhibit_filenames,
        exhibit_names_list=exhibit_names_list
    )
    print("\n--- Exhibit Result ---")
    print(exhibit_result)


    print("\n--- Combined Transcript Data ---")
    print(combined_data)

    # --------------------------------------------------
    # 7. Combine and filter for notice comparison
    # --------------------------------------------------
    keys_for_notice_comparison = [
        key.strip()
        for key in raw_keys.split(",")
        if key.strip()
    ]
    data_for_notice_comparison = {
        key: combined_data.get(key)
        for key in keys_for_notice_comparison
    }
    print("\n--- Data for Notice Comparison ---")
    print(data_for_notice_comparison)

    documentReader = DocumentReader(os.path.join(TEXT_FOLDER, NOTICE_FILENAME))
    notice_text = documentReader.read()
    notice_comparison_result = dict()
    print("Has matching notice:", hasMatchingNotice)
    emit_stage("Comparing Data With Notice...")
    if hasMatchingNotice:
        print("in hasMatchingNotice block")
        notice_comparison_result = extractor.extract_notice_comparison(
            prompt=notice_prompt.prompt,
            dict_to_compare=str(data_for_notice_comparison),
            notice_data=notice_text
        )
    else:
        print("in else block for other notice comparison")
        notice_comparison_result = extractor.extract_other_notice_comparison(
            prompt=other_notice_prompt.prompt,
            dict_to_compare=str(data_for_notice_comparison),
            notice_data=notice_text
        )
    print("\n--- Notice Comparison Result ---")
    print(notice_comparison_result)

    # --------------------------------------------------
    # RB Comparison with Fallback Logic
    # --------------------------------------------------
    emit_stage("Fetching RB Data...")
    
    # Collect available names from suffixed keys to feed the RB search
    f_list = [combined_data.get("firm_names_1"), combined_data.get("firm_names_2"), combined_data.get("firm_names_cont")]
    a_list = [combined_data.get("attorney_names_1"), combined_data.get("attorney_names_2"), combined_data.get("attorney_names_cont")]
    
    # Filter out None values or empty strings so rb.py receives a clean list of strings
    search_firms = [str(f) for f in f_list if f]
    search_attorneys = [str(a) for a in a_list if a]

    # Call RB with the aggregated lists
    rb_data = fetch_and_process_sheets(jobNo, search_firms, search_attorneys)
    
    print("====RB Data Full Map=====")
    print(rb_data)
    
    emit_stage("Comparing Data With RB...")

    if not rb_data or "contact_details" not in rb_data:
        print(f"⚠️ Warning: No RB data found for Job #{jobNo}")
        rb_comparison_result = {}
    else:
        # 1. Primary Attempt
        rb_comparison_result = extractor.extract_rb_comparison(
            prompt=rb_prompt.prompt,
            dict_to_compare=str(combined_data),
            rb_data=rb_data
        )
    print("\n--- RB Comparison Result ---")
    print(rb_comparison_result)

    # --------------------------------------------------
    # 8. Title Page Comparison Logic
    # --------------------------------------------------
    emit_stage("Comparing Data With Title Page...")
    raw_title_keys = os.getenv("KEYS_FOR_TITLE_COMPARISON", "")
    keys_for_title_comparison = [
        key.strip()
        for key in raw_title_keys.split(",")
        if key.strip()
    ]
    data_for_title_comparison = {
        key: combined_data.get(key)
        for key in keys_for_title_comparison
    }
    
    title_comparison_result = extractor.extract_title_comparison(
        prompt=title_page_prompt.prompt,
        dict_to_compare=str(data_for_title_comparison)
    )
    print("\n--- Title Comparison Result ---")
    print(title_comparison_result)

    emit_stage("Processing Complete.")

    ##### --------------------------------------------------------------

    return {
        "jobNo": jobNo,
        "combined_data": combined_data,
        "notice_comparison_result": notice_comparison_result,
        "rb_comparison_result": rb_comparison_result,
        "title_comparison_result": title_comparison_result,
        "txt_file_name": FILENAME,
        "doc_file_name": NOTICE_FILENAME,
        "isFlorida": isFlorida,
        "hasMatchingNotice": hasMatchingNotice,
        "exhibit_comparison_result": exhibit_result
    }

if __name__ == "__main__":
    process_documents(
        TEXT_FOLDER="C:\\Users\\MuhammadEhsaanurRahe\\Downloads\\Scripts\\Parser Program\\Sample 2.0\\2",
        FILENAME="119698.flood.mark.01072025.txt",
        NOTICE_FILENAME="NOD Mark Flood.pdf",
        jobNo="119698",
        hasMatchingNotice=True
    )