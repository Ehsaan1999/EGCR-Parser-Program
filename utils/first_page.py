import re

def get_page_content(file_lines, page_map, target_page_number):
    """
    Retrieves lines for a page with a look-back buffer.
    """
    if target_page_number not in page_map:
        return None

    start_idx, end_idx = page_map[target_page_number]
    
    # Look back 1 lines to ensure we capture the start of the page
    buffer_start = max(0, start_idx - 1)
    
    if buffer_start >= len(file_lines):
        return []
    return file_lines[buffer_start:end_idx]

def extract_clean_first_line(page_lines):
    """
    Finds the first meaningful line, skips standalone numbers, 
    and removes the leading '1' if present.
    """
    if not page_lines:
        return None

    for line in page_lines:
        stripped_line = line.strip()
        
        # 1. Skip Empty Lines
        if not stripped_line:
            continue
            
        # 2. Skip Pure Page Numbers (e.g. "0004")
        if stripped_line.isdigit():
            continue

        # 3. Check for '1' at the start
        # Regex update: Matches "1" followed optionally by "." or ":" or just whitespace
        match = re.match(r"^1[.:]?\s+(?P<content>.*)", stripped_line)
        
        if match:
            return match.group("content").strip()
        
        # If text doesn't start with '1', return as is
        return stripped_line

    return None

def find_transcript_start_page(file_lines, page_map, is_depo_euo_cona=False):
    """
    Iterates through pages (SKIPPING PAGES 1 and 2).
    Returns the page number of the FIRST page matching the keywords.
    """
    
    KEYWORDS = [
        "remote", "hybrid", "30(b)(6)", "videoconference", "videotaped",
        "excerpt of the", "excerpts of the", "continuation of the", "volume",
        "confidential", "deposition of", "deposition  of", "hearing", "arbitration",
        "certificate of non-appearance of", "examination under oath", "euo",
        "audio transcription", "jury trial", "trial", "interview",
        "p r o c e e d i n g s" 
    ]

    # --- NEW GUARDRAIL ---
    # If scout detected a Depo/EUO/CONA, remove "proceedings" from the start-triggers
    if is_depo_euo_cona:
        KEYWORDS = [kw for kw in KEYWORDS if kw != "p r o c e e d i n g s"]

    # Filter strictly for pages >= 3
    sorted_pages = sorted([p for p in page_map.keys() if p >= 3])

    for page_num in sorted_pages:
        lines = get_page_content(file_lines, page_map, page_num)
        clean_text = extract_clean_first_line(lines)
        
        if clean_text:
            clean_text_lower = clean_text.lower()
            for kw in KEYWORDS:
                if kw in clean_text_lower:
                    return page_num, clean_text

    return None, None