import os


def build_page_map(full_text_lines, selected, position):
    """
    Build a hashmap:
        page_number -> (start_line, end_line)

    start_line and end_line are 1-based indices.
    The page-number line itself is NOT included.
    """

    if not selected:
        return {}

    selected_sorted = sorted(selected, key=lambda x: x[1])
    total_lines = len(full_text_lines)
    page_map = {}

    if position == "TOP":
        # ----------------------------------------
        # TOP-ALIGNED PAGE NUMBERS
        # Page N:
        #   starts AFTER its page-number line
        #   ends BEFORE next page-number line
        # ----------------------------------------
        for i, (page_num, line_idx, _) in enumerate(selected_sorted):

            start_line = line_idx + 2  # exclude page number line

            if i < len(selected_sorted) - 1:
                next_page_idx = selected_sorted[i + 1][1]
                end_line = next_page_idx  # up to line before next page number
            else:
                end_line = total_lines

            if start_line <= end_line:
                page_map[page_num] = (start_line, end_line)

    else:
        # ----------------------------------------
        # BOTTOM-ALIGNED PAGE NUMBERS
        # Page N:
        #   starts AFTER previous page-number line
        #   ends BEFORE its page-number line
        # ----------------------------------------
        prev_page_line_idx = -1

        for page_num, line_idx, _ in selected_sorted:

            start_line = prev_page_line_idx + 2
            end_line = line_idx  # exclude current page number line

            if start_line <= end_line:
                page_map[page_num] = (start_line, end_line)

            prev_page_line_idx = line_idx

        # ----------------------------------------
        # HANDLE TRAILING CONTENT AFTER LAST PAGE
        # ----------------------------------------
        last_page_num, last_page_line_idx, _ = selected_sorted[-1]

        trailing_start = last_page_line_idx + 2
        trailing_end = total_lines

        has_content = any(
            line.strip()
            for line in full_text_lines[trailing_start - 1:trailing_end]
        )

        if has_content:
            page_map[last_page_num + 1] = (trailing_start, trailing_end)

    return page_map



def write_results_to_file(results, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write("=" * 60 + "\n")
            f.write(f"File: {os.path.basename(r['file'])}\n")
            f.write("=" * 60 + "\n")

            if not r["selected"]:
                f.write("No valid page numbers detected.\n\n")
                continue

            nums = [n for n, _, _ in r["selected"]]
            lines = [i + 1 for _, i, _ in r["selected"]]

            f.write(f"Page numbers: {nums}\n")
            f.write(f"Found at lines: {lines}\n")
            f.write(f"Position: {r['position']}\n")
            f.write(f"Alignment: {r['alignment']}\n")
            f.write(f"max_pos: {r['max_pos']}\n\n")

            f.write("Page Map (page -> (start_line, end_line)):\n")
            for page_num in sorted(r["page_map"]):
                start, end = r["page_map"][page_num]
                f.write(f"  Page {page_num}: lines {start}–{end}\n")

            f.write("\n\n")
