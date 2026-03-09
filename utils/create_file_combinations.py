import os
from typing import List, Dict

def create_file_combinations(folder_path: str) -> List[Dict[str, str]]:
    """
    Creates combinations of transcript TXT files and their corresponding
    notice files (PDF/DOC/DOCX) inside a folder.
    """

    if not os.path.isdir(folder_path):
        return []
        
    all_files = os.listdir(folder_path)
    txt_files = [f for f in all_files if f.lower().endswith(".txt")]
    notice_files = [f for f in all_files if f.lower().endswith((".pdf", ".doc", ".docx"))]
    
    if not txt_files or not notice_files:
        return []

    notice_paths = {f: os.path.join(folder_path, f) for f in notice_files}
    default_notice_path = notice_paths[notice_files[0]]
    
    results = []
    
    for txt_file in txt_files:
        txt_path = os.path.join(folder_path, txt_file)
        parts = txt_file.split(".")
        if len(parts) < 4:
            continue

        job_no = parts[0]
        last_name = parts[1].lower()
        first_name = parts[2].lower()

        matched_notice_path = None
        # --- FIX: Initialize the flag as False for every TXT file ---
        has_matching_notice = False 

        for notice_file in notice_files:
            notice_lower = notice_file.lower()

            # Check for BOTH names in the notice filename
            if last_name in notice_lower and first_name in notice_lower:
                matched_notice_path = notice_paths[notice_file]
                # --- FIX: Set to True if a specific match is found ---
                has_matching_notice = True 
                break

        # Fallback logic
        if not matched_notice_path:
            matched_notice_path = default_notice_path

        results.append({
            "folder_path": folder_path,
            "txt_path": txt_path,
            "notice_path": matched_notice_path,
            "jobNo": job_no,
            "hasMatchingNotice": has_matching_notice
        })

    return results

# Usage
if __name__ == "__main__":
    combos = create_file_combinations("C:/Users/MuhammadEhsaanurRahe/Downloads/Scripts/Parser Program/Sample 2.0/7")
    for c in combos:
        print(c)