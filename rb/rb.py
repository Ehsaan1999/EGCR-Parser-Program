import pandas as pd
import re
from typing import Dict, Any, List, Optional

def col_letter_to_index(letter):
    index = 0
    for char in letter.upper():
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1

def fetch_and_process_sheets(job_number: str, firm_names: List[str], attorney_names: List[str]) -> Dict[str, Any]:
    config = [
        {
            'url_id': '1s04mN8nh-n7rFZG8yPJTTKU1IGmtjZ6MBh_ggpiD3dU',
            'gid': '1546586553', # Firms/Contacts
            'cols_letters': ['A', 'C', 'D', 'E', 'F', 'G', 'O', 'T'],
            'sheet_name': 'Firms/Contacts'
        },
        {
            'url_id': '1s04mN8nh-n7rFZG8yPJTTKU1IGmtjZ6MBh_ggpiD3dU',
            'gid': '802112672', # RB Pull
            'cols_letters': ['A', 'B', 'F', 'G', 'I', 'L', 'M', 'N', 'Q', 'S', 'T', 'U', 'V'],
            'sheet_name': 'RB Pull Sample'
        }
    ]

    # --- 1. Get Job Data from RB Pull Sample ---
    rb_url = f'https://docs.google.com/spreadsheets/d/{config[1]["url_id"]}/export?format=csv&gid={config[1]["gid"]}'
    # Load, replace linebreaks with space, and strip whitespace
    df_rb_full = (pd.read_csv(rb_url, dtype=str)
                  .replace(r'\r+|\n+', ' ', regex=True)
                  .apply(lambda x: x.str.strip() if x.dtype == "object" else x))
    
    col_indices_rb = [col_letter_to_index(c) for c in config[1]['cols_letters']]
    col_names_rb = [df_rb_full.columns[i] for i in col_indices_rb if i < len(df_rb_full.columns)]
    
    df_job = df_rb_full[df_rb_full.iloc[:, 0] == str(job_number)][col_names_rb]
    
    if df_job.empty:
        return {"error": f"Job {job_number} not found in RB Sample"}

    # --- 2. Build Lookup Directory from Firms/Contacts ---
    contacts_url = f'https://docs.google.com/spreadsheets/d/{config[0]["url_id"]}/export?format=csv&gid={config[0]["gid"]}'
    # Load, replace linebreaks with space, and strip whitespace
    df_contacts_full = (pd.read_csv(contacts_url, dtype=str)
                        .replace(r'\r+|\n+', ' ', regex=True)
                        .apply(lambda x: x.str.strip() if x.dtype == "object" else x))
    
    col_indices_contacts = [col_letter_to_index(c) for c in config[0]['cols_letters']]
    col_names_contacts = [df_contacts_full.columns[i] for i in col_indices_contacts if i < len(df_contacts_full.columns)]
    df_directory = df_contacts_full[col_names_contacts]

    # --- 3. Loop and Search (Token-Based Matching) ---
    found_contacts = []

    for f_name in firm_names:
        # Strip punctuation and normalize transcript firm name
        f_name_lower = f_name.lower()
        f_name_clean = re.sub(r'[^\w\s]', '', f_name_lower)
        
        for a_name in attorney_names:
            a_parts = a_name.lower().split()
            if not a_parts:
                continue
                
            first_part = a_parts[0]
            last_part = a_parts[-1]

            # --- LOOSENED FIRM MATCH LOGIC (Punctuation Agnostic) ---
            # Checks if transcript name is in directory OR if directory name is in transcript
            # Both sides are cleaned of punctuation to handle cases like "Firm, LLP" vs "Firm LLP"
            firm_matches = df_directory[
                df_directory.iloc[:, 0].str.lower().apply(
                    lambda x: (
                        clean_x := re.sub(r'[^\w\s]', '', str(x).lower()),
                        f_name_clean in clean_x or clean_x in f_name_clean
                    )[1] if pd.notnull(x) else False
                )
            ]
            
            for _, row in firm_matches.iterrows():
                # Col O (Index 6) contains the Contact Name
                sheet_name_raw = str(row.iloc[6]).lower()
                sheet_name_parts = sheet_name_raw.split()
                
                # Verify first and last name components exist in the target name string
                if first_part in sheet_name_parts and last_part in sheet_name_parts:
                    found_contacts.append(row.to_dict())
                    print(f"Match found: Firm '{f_name}' with Attorney '{a_name}' -> Contact '{row.iloc[6]}'")

    # --- 4. Final Aggregation ---
    # Deduplicate contacts by name (keep first occurrence) to avoid LLM confusion
    seen_names = set()
    unique_contacts = []
    for contact in found_contacts:
        name_key = str(contact.get("Contact name", "")).strip().lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            unique_contacts.append(contact)

    result_hashmap = {
        "job_info": df_job.to_dict('records')[0],
        "contact_details": unique_contacts
    }

    return result_hashmap

if __name__ == "__main__":
    firmNames = ['Mitchell, Shapiro, Greenamyre & Funt, LLP', 'Georgia Resource Center', 'Georgia Resource Center', 'Georgia Attorney Generals Office'] 
    attorneyNames = ['ZACK W. GREENAMYRE', 'ANNA ARCENEAUX', 'DANIELLE KAYEMBE', 'SABRINA GRAHAM'] 
    job_no = '134564'
    
    final_data = fetch_and_process_sheets(job_no, firmNames, attorneyNames)
    import pprint
    pprint.pprint(final_data)