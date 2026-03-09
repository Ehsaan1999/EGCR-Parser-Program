exhibit_comparison_prompt = f"""
ROLE: High-Precision Legal Data Validator.

TASK: Cross-reference Exhibit Names extracted from a transcript against actual Filenames found in the directory.

LOGIC:
1. IGNORE EXTENSIONS: Ignore .pdf, .jpg, .tif, etc., during comparison.
2. EXACT MATCH: The core identifier and any description are identical (e.g., "Exhibit 1" matches "Exhibit 1.pdf").
3. PARTIAL MATCH: The exhibit identifier matches, but the description or naming convention differs (e.g., "Exhibit 1" matches "Ex. 1 - Invoice.pdf").
4. NO MATCH: The Exhibit identifier is not found anywhere in the filename list.
5. MISSING: If the transcript exhibit name is null/empty or if the filename list is empty, return "Missing".

INSTRUCTIONS:
Below this prompt, I will provide two JSON lists. 
- The FIRST JSON list contains the ACTUAL_FILENAMES.
- The SECOND JSON list contains the TRANSCRIPT_EXHIBIT_NAMES.

Map every name in the TRANSCRIPT_EXHIBIT_NAMES list to a status based on the ACTUAL_FILENAMES list. Use ONLY: "Exact Match", "Partial Match", "No Match", "Missing".

JSON OUTPUT SCHEMA
{{
  "comparisons": {{
    "Exhibit Name from Transcript": "Status"
  }}
}}
"""