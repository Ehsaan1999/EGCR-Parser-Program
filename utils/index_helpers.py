import re
from typing import List, Dict, Tuple, Optional

VALID_EXAMINATION_HEADINGS = {
    "EXAMINATION",
    "CROSS-EXAMINATION",
    "RECROSS-EXAMINATION",
    "FURTHER RECROSS-EXAMINATION",
    "DIRECT EXAMINATION",
    "REDIRECT EXAMINATION",
}

def validate_examination_headings(
    examinations_list: List[Dict[str, str]],
    page_map: Dict[int, Tuple[int, int]],
    all_lines: List[str],
) -> List[Dict[str, str]]:
    """
    Returns only the examination dictionaries that were successfully verified 
    against the transcript text.
    """
    if not examinations_list:
        return []

    valid_examinations = []

    for item in examinations_list:
        page_str = item.get("page", "")
        try:
            page_num = int(page_str)
        except (ValueError, TypeError):
            continue  # Skip items with invalid page formats

        if page_num not in page_map:
            continue

        start_line, end_line = page_map[page_num]
        page_lines = all_lines[start_line-1: end_line]

        page_has_valid_heading = False
        for line in page_lines:
            # Normalize and clean lines
            line_no_nums = re.sub(r"^\s*\d+\s*", "", line)
            line_no_nums = re.sub(r"\s*\d+\s*$", "", line_no_nums)
            normalized = re.sub(r"\s+", " ", line_no_nums).strip()

            if not normalized:
                continue

            if normalized == normalized.upper() and normalized in VALID_EXAMINATION_HEADINGS:
                page_has_valid_heading = True
                break

        # SUCCESS: If heading found, add the whole dictionary to the success list
        if page_has_valid_heading:
            valid_examinations.append(item)

    return valid_examinations

def validate_exhibits_headings(
    exhibits_list: List[Dict[str, str]],
    page_map: Dict[int, Tuple[int, int]],
    all_lines: List[str],
) -> List[Dict[str, str]]:
    """
    Returns only the exhibit dictionaries that were successfully verified 
    against the transcript text.
    """
    if not exhibits_list:
        return []

    valid_exhibits = []
    valid_patterns = [
        r"Plaintiff's Exhibit \d+ was marked for identification",
        r"Plaintiff's Exhibit \d+ was introduced",
        r"Plaintiff's Exhibit \d+ was marked",
        r"Petitioner's Exhibit \d+ was admitted into evidence",
        r"Petitioner's Exhibit \d+ was marked for identification",
        r"Petitioner's \d+ was marked for identification"
    ]
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in valid_patterns]

    for item in exhibits_list:
        page_str = item.get("page", "")
        try:
            page = int(page_str)
        except (ValueError, TypeError):
            continue

        if page not in page_map:
            continue

        start_idx, end_idx = page_map[page]
        page_lines = all_lines[start_idx:end_idx]

        found = False
        i = 0
        while i < len(page_lines):
            if not page_lines[i].strip():
                i += 1
                continue

            line_clean = re.sub(r"^\s*\d+\s*", "", page_lines[i]).strip()

            if any(p.search(line_clean) for p in compiled_patterns):
                found = True
                break

            # Look ahead logic for multi-line phrases
            j = i + 1
            while j < len(page_lines) and not page_lines[j].strip():
                j += 1
            if j < len(page_lines):
                next_line_clean = re.sub(r"^\s*\d+\s*", "", page_lines[j]).strip()
                combined = f"{line_clean} {next_line_clean}"
                if any(p.search(combined) for p in compiled_patterns):
                    found = True
                    break
            i += 1

        # SUCCESS: If pattern found, add the whole dictionary to the success list
        if found:
            valid_exhibits.append(item)

    return valid_exhibits