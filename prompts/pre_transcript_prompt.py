from datetime import datetime

# 1. Get the actual real-time date
actual_today = datetime.now().strftime("%Y-%m-%d")

prompt = f"""
Im going to send you a legal transcript. Extract the following into JSON and remove all linespaces and line breaks while doing so:

Page 1: Title Page
1. court_heading,
2. case_number,
3. case_style,
4. job_title, (Only extract the title of the job, do NOT include any names. For example, if the title is "HEARING BEFORE THE HONORABLE STACEY K. HYDRICK", only extract "HEARING BEFORE THE HONORABLE" and so on.)
5. witness_name, (only the name, no titles)
6. job_date,
7. current_date: Use and store the value from "{actual_today}". Do not attempt to guess or extract this from the transcript.
8. start_time,
9. location, (complete address if present)
10. resource name (only the name)

Page 2: Appearances Page

APPEARANCES: Scan the "Appearances" page and the "Also Present" section.

INCLUSIVITY: Extract ALL individuals listed, including Attorneys, Paralegals, and Firm Employees except videographers/court reporters.

MAPPING: Assign them to attorney_names_1, _2, and use _cont for everyone thereafter. If they are not attorneys, treat their "Role/Title" (e.g., Employee) as their representation status.

11. appearances_present: (True/False).
12. esquire_check_1, esquire_check_2: "[attorney_names_1/2], Esquire" or "[attorney_names_1/2], Esq." or "[attorney_names_1/2], ESQ." or anything similar for the first two attorneys (if present).
13. esquire_check_cont: Fraction for remaining attorneys (e.g., "2/2").
14. For the first two attorneys, return individual strings:
    - attorney_names_1, attorney_names_2 (No 'Esquire')
    - attorney_representation_1, attorney_representation_2
    - firm_names_1, firm_names_2, firm_address_1, firm_address_2, firm_city_1, firm_city_2
    - firm_state_1, firm_state_2, firm_zip_1, firm_zip_2
    - phone_numbers_1, phone_numbers_2 (just the numbers, no special characters or facimile)
    - emails_1, emails_2
15. For any additional attorneys (3rd onwards), return parallel lists:
    - attorney_names_cont, firm_names_cont, emails_cont, etc. (Return null if no 3rd attorney exists).
    

Page 3: Index Page
16. index_witness_name, (only the name, no titles),
17. index_to_examinations_proceedings_present,
18. index_to_examinations_proceedings_heading,
19. index_to_exhibits_present,
20. index_to_exhibits_heading,
21. index_to_exhibits_retained, (Check if the word "Retained" appears in the Index to Exhibits page. Return True/False).
22. examinations_proceedings_page_numbers (List of objects, do not include description, just the numbers or names),
23. exhibits_page_numbers (In exhibit name format, e.g., "Exhibit 1", "Exhibit A", etc. Do not include page numbers if they are listed in the same line as the exhibit name,,
24. exhibit_parenthetical.

Page 4: Transcript 1st Page
25. transcript_job_title, (Only extract the title of the job, do NOT include any names. For example, if the title is "HEARING BEFORE THE HONORABLE STACEY K. HYDRICK", only extract "HEARING BEFORE THE HONORABLE" and so on).
26. transcript_witness_name, (only the name, no titles on transcript page)
27. transcript_date, (date on transcript page)
28. duly_sworn (True/False from transcript page).
"""