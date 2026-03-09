prompt = """
I will send you a legal transcript. 
I want you to extract the following key items and return them in a simplified JSON format. 
Do not include fields for page numbers, full parentheticals, or section headings (only boolean presence checks).

Extracted Items:

End Time (e.g., 11:06 AM)

Signature Status (Waived or Reserved)

'Certificate of Reporter/Transcriber' page Heading Presence (Boolean: Present/Not Present)

'Certificate of Reporter/Transcriber' page Court Subheading Presence (Boolean: Present/Not Present)

'Certificate of Reporter/Transcriber' Page Date (Will be present around the end of the page - e.g., 16th day of April 2025)

'Certificate of Reporter/Transcriber' Page Resource Name (Will be present at the end of the page - only the name of the resource, do not include any other codes/information)

'Certificate of Oath/Notary Public' Page Presence (Boolean: Present/Not Present)

'Certificate of Oath/Notary Public' Page Date (Will be present around the end of the page - e.g., 16th day of April 2025)

'Certificate of Oath/Notary Public' Page Resource Name (Will be present at the end of the page - confirm if Notary Public is present, if not, return Missing)

'Disclosure of No Contract' Page Presence (Boolean: Present/Not Present)

'Disclosure of No Contract' Page Date (Will be present around the end of the page - e.g., 16th day of April 2025)

'Disclosure of No Contract' Page Resource Name (Will be present at the end of the page - only the name of the resource, do not include any other codes/information)
"""