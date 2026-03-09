prompt = """
I will send you a legal transcript. 
Extract the following into JSON and remove all linespaces and line breaks while doing so.
Do not include fields for page numbers, full parentheticals, or section headings (only boolean presence checks).

Extracted Items:

- End Time (e.g., 11:06 AM)

- Signature Status (Waived or Reserved)

- 'Certificate' page Heading Presence in Uppercase (Boolean: Present/Not Present). Acceptable headings:
“CERTIFICATE”
“C E R T I F I C A T E”
“REPORTER'S CERTIFICATE”
“COURT REPORTER'S CERTIFICATE”

- 'Certificate' Page Heading returned. Check for: “CERTIFICATE”, “REPORTER'S CERTIFICATE”, etc.

- 'Certificate' page Court Subheading Presence in Uppercase (Boolean: Present/Not Present). Check for:
“State of _____:”
“County of ______:”

- 'Certificate' Page Date (Will be present around the end of the page - e.g., 16th day of April 2025)

- 'Certificate' Page Resource Name (Will be present at the end of the page - only the name of the resource, do not include any other codes/information)

- 'Disclosure of No Contract' Page Presence in Uppercase (Boolean: Present/Not Present). Acceptable headings:
“DISCLOSURE OF NO CONTRACT”
"DISCLOSURE"

- 'Disclosure of No Contract' Page Heading in returned. Check for: “DISCLOSURE OF NO CONTRACT”, "DISCLOSURE" , etc.

- 'Disclosure of No Contract' Page Date (Will be present around the end of the page - e.g., 16th day of April 2025)

- 'Disclosure of No Contract' Page Resource Name (Will be present at the end of the page - only the name of the resource, do not include any other codes/information)

"""