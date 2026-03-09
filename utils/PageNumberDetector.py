import os
import re
from utils.build_page_map import build_page_map


class PageNumberDetector:
    """
    Detects page numbers in text files and builds page maps.
    """

    PAGE_NUM_REGEX = re.compile(r'^\s*(\d{1,6})\s*$')

    def __init__(
        self,
        text_folder,
        min_gap_lines=25,
        enforce_left_pad_format=True
    ):
        self.text_folder = text_folder
        self.min_gap_lines = min_gap_lines
        self.enforce_left_pad_format = enforce_left_pad_format

    # --------------------------------------------------
    # Core helpers
    # --------------------------------------------------

    @staticmethod
    def is_line_blank(raw):
        return not raw.strip()

    @staticmethod
    def compute_start_index(raw_line):
        raw = raw_line.rstrip("\n")
        stripped = raw.strip()
        return raw.index(stripped) if stripped else 0

    @staticmethod
    def compute_max_non_ws_pos(lines):
        max_pos = 0
        for raw in lines:
            stripped_r = raw.rstrip("\n").rstrip()
            if stripped_r:
                last_non_space_index = len(stripped_r) - 1
                max_pos = max(max_pos, last_non_space_index + 1)
        return max_pos if max_pos > 0 else 1

    # --------------------------------------------------
    # Detection logic
    # --------------------------------------------------

    def find_numeric_candidates(self, lines):
        """
        Returns list of (page_num, line_index, raw_line)
        for lines that contain only a number.
        """
        candidates = []
        for idx, raw in enumerate(lines):
            m = self.PAGE_NUM_REGEX.match(raw)
            if not m:
                continue
            num_str = m.group(1)
            if not (1 <= len(num_str) <= 5):
                continue
            num = int(num_str)
            if num < 1:
                continue
            candidates.append((num, idx, raw))
        return candidates
        #         candidates.append((int(m.group(1)), idx, raw))
        # return candidates

    def select_page_numbers(self, candidates):
        """
        Applies sequence, spacing, alignment, and format heuristics.
        """
        if not candidates:
            return []

        selected = []

        prev_num, prev_idx, prev_raw = candidates[0]
        prev_start = self.compute_start_index(prev_raw)
        selected.append((prev_num, prev_idx, prev_raw, prev_start))

        first_line_length = len(prev_raw.strip())
        left_aligned = prev_start == 0

        for num, idx, raw in candidates[1:]:
            # 1. Sequential numbering
            if num != prev_num + 1:
                continue

            # 2. Minimum spacing
            if (idx - prev_idx) < self.min_gap_lines:
                continue

            # 3. Alignment tolerance
            current_start = self.compute_start_index(raw)
            digit_shift = abs(len(str(prev_num)) - len(str(num)))
            tolerance = 4 + digit_shift

            if abs(current_start - prev_start) > tolerance:
                continue

            # 4. Optional left-pad format guardrail
            if self.enforce_left_pad_format and left_aligned:
                if len(raw.strip()) != first_line_length:
                    continue

            selected.append((num, idx, raw, current_start))

            prev_num = num
            prev_idx = idx
            prev_raw = raw
            prev_start = current_start

        # Strip start-index column before returning
        return [(n, i, raw) for (n, i, raw, _) in selected]

    # --------------------------------------------------
    # Page placement logic
    # --------------------------------------------------

    def determine_position(self, lines, page_idx):
        """
        Determines whether page numbers are TOP or BOTTOM aligned.
        """
        for i in range(page_idx):
            if not self.is_line_blank(lines[i]):
                return "BOTTOM"
        return "TOP"

    def determine_alignment(self, lines, first_raw):
        max_pos = self.compute_max_non_ws_pos(lines)
        raw_line = first_raw.rstrip("\n")
        stripped = raw_line.strip()
        start_index = raw_line.index(stripped)

        left_threshold = 0.25 * max_pos
        right_threshold = 0.75 * max_pos

        if start_index <= left_threshold:
            return "LEFT"
        elif start_index >= right_threshold:
            return "RIGHT"
        return "CENTER"

    # --------------------------------------------------
    # File-level analysis
    # --------------------------------------------------

    def analyze_file(self, filepath):
        print(f"\n=== Processing: {filepath} ===")

        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()

        total_lines = len(lines)
        candidates = self.find_numeric_candidates(lines)
        selected = self.select_page_numbers(candidates)

        if not selected:
            print("No valid page-number sequence found.")
            return {
                "file": filepath,
                "total_lines": total_lines,
                "selected": [],
                "position": None,
                "alignment": None,
                "max_pos": None,
                "page_map": {}
            }

        accepted_nums = [n for n, _, _ in selected]
        accepted_lines = [i + 1 for _, i, _ in selected]

        # print(f"Accepted page numbers: {accepted_nums}")
        # print(f"Accepted page-number lines: {accepted_lines}")

        first_num, first_idx, first_raw = selected[0]
        position = self.determine_position(lines, first_idx)
        alignment = self.determine_alignment(lines, first_raw)

        page_map = build_page_map(
            full_text_lines=lines,
            selected=selected,
            position=position
        )

        return {
            "file": filepath,
            "total_lines": total_lines,
            "position": position,
            "alignment": alignment,
            "max_pos": self.compute_max_non_ws_pos(lines),
            "page_map": page_map
        }

    # --------------------------------------------------
    # Driver
    # --------------------------------------------------

    def run(self, filename_filter=None):
        # results = []

        # for fname in sorted(os.listdir(self.text_folder)):
            # if not fname.lower().endswith(".txt"):
            #     continue

            # if filename_filter and fname.lower() != filename_filter.lower():
                # continue

        filepath = os.path.join(self.text_folder, filename_filter)
        res = self.analyze_file(filepath)
        # results.append(res)

        print("\n==============================")
        print(f"File: {filename_filter}")
        print("==============================")
        return res
