from operator import index
import os
from unittest import result
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

# --- 1. CONFIGURATION & HELPERS ---

SECTIONS = [
    ("Title Page", ["court_heading", "case_number", "case_style", "job_title", "witness_name", "job_date", "start_time", "location", "resource"]),
    ("First Appearance", ["esquire_check_1", "attorney_representation_1", "attorney_names_1", "firm_names_1", "firm_address_1", "firm_city_1", "firm_state_1", "firm_zip_1", "phone_numbers_1", "emails_1"]),
    ("Second Appearance", ["esquire_check_2", "attorney_representation_2", "attorney_names_2",  "firm_names_2", "firm_address_2", "firm_city_2", "firm_state_2", "firm_zip_2", "phone_numbers_2", "emails_2"]),
    ("Appearances Cont.", ["esquire_check_cont", "attorney_representation_cont", "attorney_names_cont", "firm_names_cont", "firm_address_cont", "firm_city_cont", "firm_state_cont", "firm_zip_cont", "phone_numbers_cont", "emails_cont"]),
    ("Indices Pages", ["index_witness_name", "index_to_examinations_proceedings_present", "index_to_examinations_proceedings", "index_to_exhibits_present", "exhibit_parenthetical", "index_to_exhibits", "exhibit_file_count"]),
    ("Body Details", ["transcript_job_title", "transcript_witness_name", "transcript_date", "duly_sworn", "end_time", "signature_status"]),
    ("Closing Details", ["disclosure_page_present", "disclosure_heading", "disclosure_date", "disclosure_resource_name", "certificate_heading_present", "certificate_heading", "court_subheading_present", "court_subheading", "certificate_date", "certificate_resource_name"])
]

SECTIONS_FLORIDA = [
    ("Title Page", ["court_heading", "case_number", "case_style", "job_title", "witness_name", "job_date", "start_time", "resource", "notary_public_check", "location"]),
    ("First Appearance", ["esquire_check_1", "attorney_representation_1", "attorney_names_1", "firm_names_1", "firm_address_1", "firm_city_1", "firm_state_1", "firm_zip_1", "phone_numbers_1", "emails_1"]),
    ("Second Appearance", ["esquire_check_2", "attorney_representation_2", "attorney_names_2",  "firm_names_2", "firm_address_2", "firm_city_2", "firm_state_2", "firm_zip_2", "phone_numbers_2", "emails_2"]),
    ("Appearances Cont.", ["esquire_check_cont", "attorney_representation_cont", "attorney_names_cont", "firm_names_cont", "firm_address_cont", "firm_city_cont", "firm_state_cont", "firm_zip_cont", "phone_numbers_cont", "emails_cont"]),
    ("Indices Pages", ["index_witness_name", "index_to_examinations_proceedings_present", "index_to_examinations_proceedings", "index_to_exhibits_present", "exhibit_parenthetical", "index_to_exhibits", "exhibit_file_count"]),
    ("Body Details", ["transcript_job_title", "transcript_witness_name", "transcript_date", "duly_sworn", "end_time", "signature_status"]),
    ("Closing Details", ["disclosure_page_present", "disclosure_heading", "disclosure_date", "disclosure_resource_name", "oath_certificate_page_present", "oath_certificate_heading", "oath_court_subheading_present", "oath_certificate_page_date", "oath_certificate_resource_name", "certificate_heading_present", "certificate_heading", "court_subheading_present", "court_subheading", "certificate_date", "certificate_resource_name"])
]

NOTICE_EXCEPTIONS = [
    "resource", "notary_public_check", "esquire_check_1", "esquire_check_2", 
    "end_time", "signature_status", "index_to_examinations_proceedings_present","index_to_examinations_proceedings",
    "index_to_exhibits_present", "index_to_exhibits", "exhibit_file_count", "disclosure_page_present", 
    "disclosure_resource_name", "certificate_heading_present",
    "court_subheading_present", "certificate_resource_name", "oath_certificate_page_present",
    "oath_court_subheading_present", "oath_certificate_resource_name",
    "index_to_examinations_proceedings_present", "index_to_exhibits_present", "exhibit_parenthetical",
    "duly_sworn", "index_witness_name",
    "esquire_check_cont",
]

OTHER_NOTICE_EXCEPTIONS = [
    "job_title", "witness_name", "start_time", "phone_numbers_1", "phone_numbers_2", 
    "emails_1", "emails_2", "index_witness_name", "resource", "esquire_check_1", "esquire_check_2", 
    "end_time", "signature_status", "index_to_examinations_proceedings_present","index_to_examinations_proceedings",
    "index_to_exhibits_present","index_to_exhibits",
    "exhibit_parenthetical", "exhibit_file_count", "disclosure_page_present", "disclosure_date", 
    "disclosure_resource_name", "certificate_heading_present", "court_subheading_present", 
    "certificate_date", "certificate_resource_name", "oath_certificate_page_present", 
    "oath_court_subheading_present", "oath_certificate_resource_name",
    "index_to_examinations_proceedings_present", "index_to_exhibits_present",
    "transcript_job_title", "transcript_witness_name", "transcript_date", "duly_sworn",
    "esquire_check_cont", "attorney_representation_cont",
    "phone_numbers_cont", "emails_cont"
]
RB_EXCEPTIONS = [
    "notary_public_check", "attorney_representation_1", "attorney_representation_2", 
    "esquire_check_1", "esquire_check_2", "index_witness_name",
    "index_to_examinations_proceedings_present", "index_to_examinations_proceedings",
    "index_to_exhibits_present", "index_to_exhibits", "exhibit_file_count", "disclosure_page_present", "disclosure_heading",
    "certificate_heading_present", "certificate_heading", "court_subheading_present", "court_subheading",
    "oath_certificate_page_present", "oath_court_subheading_present", "oath_certificate_page_date", 
    "oath_certificate_resource_name", "index_to_examinations_proceedings_present", 
    "index_to_exhibits_present", "exhibit_parenthetical", 
    "duly_sworn", "esquire_check_cont", "attorney_representation_cont"
]

def get_status_info(text):
    text = str(text).strip().lower()
    if any(term in text for term in ["exact", "verified", "none"]) or text == "n/a": 
        return colors.HexColor("#228B22"), "✔ "
    elif "partial" in text: 
        return colors.HexColor("#FF8C00"), "! "
    elif "no match" in text: 
        return colors.HexColor("#DC143C"), "✘ "
    elif "missing" in text or not text or "✘" in text: 
        return colors.HexColor("#8B0000"), "✘ "
    elif text == "-": 
        return colors.black, ""
    return colors.black, ""

def format_label(field_name):
    # Mapping for new schema variables and specific formatting
    special_labels = {
        "title_date": "Job Date",
        "job_title_heading": "Job Title Heading",
        "witness_name": "Witness Name",
        "transcript_date": "Transcript Date"
    }
    if field_name in special_labels:
        return special_labels[field_name]
        
    label = field_name.replace('_1', '').replace('_2', '').replace('_cont', '')
    return label.replace('_', ' ').title()

def calculate_stats(data_dict, fields_to_check, exception_list, combined_data=None):
    stats = {"Exact": 0, "Partial": 0, "No Match": 0, "Missing": 0}
    combined_data = combined_data or {}

    for field in fields_to_check:
        base_f = field.replace('_1', '').replace('_2', '').replace('_cont', '')
        if field in exception_list or base_f in exception_list: 
            continue
        
        if base_f in ["index_to_examinations_proceedings", "index_to_exhibits"]:
            source_key = "examinations_proceedings_page_numbers" if base_f == "index_to_examinations_proceedings" else "exhibits_page_numbers"
            sub_items = combined_data.get(source_key) or []
            failed_pages = data_dict.get(base_f, [])
            for item in sub_items:
                if str(item.get('page')) in map(str, failed_pages): stats["No Match"] += 1
                else: stats["Exact"] += 1
            continue

        val = data_dict.get(field, "")
        if isinstance(val, str) and "/" in val:
            try:
                parts = val.split('/')
                num, den = int(parts[0]), int(parts[1])
                if num == den and den > 0: stats["Exact"] += 1
                elif num == 0: stats["No Match"] += 1
                else: stats["Partial"] += 1
                continue
            except: pass

        if isinstance(val, list):
            for item in val:
                v_str = str(item).lower()
                if "exact" in v_str: stats["Exact"] += 1
                elif "no match" in v_str: stats["No Match"] += 1
                elif "partial" in v_str: stats["Partial"] += 1
                elif "missing" in v_str:
                    if base_f not in ["certificate_date", "disclosure_date"]:
                        stats["Missing"] += 1
            continue

        val_str = str(val).strip().lower()
        if val_str in ["-", "n/a", "", "none"]: continue
        
        if "exact" in val_str or "verified" in val_str: stats["Exact"] += 1
        elif "partial" in val_str: stats["Partial"] += 1
        elif "no match" in val_str: stats["No Match"] += 1
        elif "missing" in val_str: 
            if base_f not in ["certificate_date", "disclosure_date"]:
                stats["Missing"] += 1
            
    return stats

def create_multi_page_report(unique_id, output_dir, combined_results):
    try:
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f"QC Report {unique_id}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=(8.5*inch, 11*inch), topMargin=0.2*inch, bottomMargin=0.2*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=11, spaceAfter=2)
        sub_title_style = ParagraphStyle('SubTitle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=8, spaceBefore=4, spaceAfter=2)
        section_head_style = ParagraphStyle('SectionHead', parent=styles['Heading3'], alignment=TA_CENTER, fontSize=7, backColor=colors.lightgrey, spaceBefore=10, spaceAfter=2)
        head_text = ParagraphStyle('HeadText', fontSize=7, fontName='Helvetica-Bold', alignment=TA_CENTER)
        body_text = ParagraphStyle('BodyText', fontSize=6.5, leading=8, alignment=TA_CENTER)

        table_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ])

        elements = []

        for idx, result in enumerate(combined_results):
            c_data = result.get('combined_data', {})
            rb_res = result.get('rb_comparison_result', {})
            n_res = result.get('notice_comparison_result', {})
            tp_res = result.get('title_comparison_result', {}) 
            is_fla = result.get('isFlorida', False)
            has_notice = result.get('hasMatchingNotice', False)
            exh_result = result.get('exhibit_comparison_result', {}).get('comparisons', {})            
            current_sections = SECTIONS_FLORIDA if is_fla else SECTIONS
            current_fields_list = [f for sec in current_sections for f in sec[1]]
            active_notice_exc = NOTICE_EXCEPTIONS if has_notice else OTHER_NOTICE_EXCEPTIONS

            elements.append(Paragraph(f"<u>Gallo QC Report - Job {unique_id}</u>", title_style))

            txt_fn = result.get('txt_file_name', '')
            doc_fn = result.get('doc_file_name', '')
            elements.append(Paragraph(f"Transcript: {txt_fn}  |  Notice: {doc_fn}", sub_title_style))

            summary_configs = [("Notice", n_res, active_notice_exc), ("RB", rb_res, RB_EXCEPTIONS)]

            for sec_name, fields in current_sections:
                if sec_name == "Second Appearance" and not c_data.get("attorney_names_2"): 
                    continue
                
                if sec_name == "Appearances Cont.":
                    if not any(val for field in fields if (val := c_data.get(field)) and str(val).strip() not in ["0/0", "None", "n/a"]):
                        continue

                if sec_name == "Indices Pages":
                    elements.append(Paragraph("Index to Examinations/Proceedings", section_head_style))
                    proc_headers = [Paragraph("Element", head_text), Paragraph("Transcript", head_text), Paragraph("Page", head_text), Paragraph("Status", head_text)]
                    proc_rows = [proc_headers]
                    
                    p_present = c_data.get("index_to_examinations_proceedings_present")
                    p_match_raw = n_res.get("index_to_examinations_proceedings") or rb_res.get("index_to_examinations_proceedings") or ("Exact Match" if p_present else "Missing")
                    p_col, p_icon = get_status_info(p_match_raw)
                    index_to_examinations_proceedings_heading = c_data.get("index_to_examinations_proceedings_heading")
                    
                    proc_rows.append([
                        Paragraph("Examinations/Proceedings Heading Present", body_text),
                        Paragraph(str(p_present).upper() if p_present else "<font color='black'>Missing</font>", body_text),
                        Paragraph("-", body_text),
                        Paragraph(f"<font color='{p_col}'>{p_icon}{p_match_raw}</font>", body_text)
                    ])

                    index_to_examinations_proceedings_heading_check = tp_res.get("index_to_examinations_proceedings_heading_check")
                    p_col, p_icon = get_status_info(index_to_examinations_proceedings_heading_check)
                    
                    proc_rows.append([
                        Paragraph("Index Heading", body_text),
                        Paragraph(index_to_examinations_proceedings_heading if p_present else "<font color='black'>Missing</font>", body_text),
                        Paragraph("-", body_text),
                        Paragraph(f"<font color='{p_col}'>{p_icon}{index_to_examinations_proceedings_heading_check}</font>", body_text)
                    ])
                    
                    w_name = c_data.get("index_witness_name")
                    w_match_raw = tp_res.get("index_witness_name")
                    
                    if str(w_match_raw).lower() == "missing":
                        m_col, m_icon = colors.black, ""
                    else:
                        m_col, m_icon = get_status_info(w_match_raw)
                    
                    proc_rows.append([
                        Paragraph("Index Witness Name", body_text),
                        Paragraph(w_name if w_name else "<font color='#8B0000'>✘ Missing</font>", body_text),
                        Paragraph("-", body_text),
                        Paragraph(f"<font color='{m_col}'>{m_icon}{w_match_raw}</font>", body_text)
                    ])
                    
                    for item in (c_data.get("examinations_proceedings_page_numbers") or []):
                        p_num = str(item.get('page', ''))
                        proc_rows.append([
                            Paragraph("Examination Page", body_text),
                            Paragraph(f"{item.get('name', '')}, Page {p_num}", body_text),
                            Paragraph(p_num, body_text),
                            Paragraph("<font color='#228B22'>✔ Exact Match</font>", body_text)
                        ])
                    
                    add_exams = c_data.get("additional_examinations_found", [])
                    if not add_exams:
                        proc_rows.append([
                            Paragraph("Additional Examinations found?", body_text), 
                            Paragraph("<font color='#228B22'>None</font>", body_text), 
                            Paragraph("<font color='#228B22'>N/A</font>", body_text), 
                            Paragraph("<font color='#228B22'>✔ Exact Match</font>", body_text)
                        ])
                    else:
                        for exam in add_exams:
                            proc_rows.append([
                                Paragraph("Additional Examinations found?", body_text),
                                Paragraph(f"<font color='#8B0000'>{exam.get('text', '✘ Missing')}</font>", body_text),
                                Paragraph(f"<font color='#8B0000'>{exam.get('page', '✘ Missing')}</font>", body_text),
                                Paragraph("<font color='#8B0000'>✘ Missing</font>", body_text)
                            ])

                    t_proc = Table(proc_rows, colWidths=[1.3*inch, 3.2*inch, 0.8*inch, 1.2*inch])
                    t_proc.setStyle(table_style)
                    elements.append(t_proc)
                    elements.append(Spacer(1, 0.2*inch))

                    elements.append(Paragraph("Index to Exhibits", section_head_style))
                    exh_headers = [Paragraph("Element", head_text), Paragraph("Transcript", head_text), Paragraph("File", head_text), Paragraph("Page", head_text), Paragraph("Status", head_text)]
                    exh_rows = [exh_headers]
                    
                    e_present = c_data.get("index_to_exhibits_present")
                    e_match_raw = n_res.get("index_to_exhibits") or rb_res.get("index_to_exhibits") or ("Exact Match" if e_present else "Missing")
                    e_col, e_icon = get_status_info(e_match_raw)
                    index_to_exhibits_heading = c_data.get("index_to_exhibits_heading")

                    exh_rows.append([
                        Paragraph("Exhibit Index Heading Present", body_text),
                        Paragraph(str(e_present).upper() if e_present else "<font color='black'>Missing</font>", body_text),
                        Paragraph("-", body_text), Paragraph("-", body_text),
                        Paragraph(f"<font color='{e_col}'>{e_icon}{e_match_raw}</font>", body_text)
                    ])

                    exh_rows.append([
                        Paragraph("Exhibit Index Heading", body_text),
                        Paragraph(index_to_exhibits_heading if e_present else "<font color='#8B0000'>✘ Missing</font>", body_text),
                        Paragraph("-", body_text), Paragraph("-", body_text),
                        Paragraph(f"<font color='{e_col}'>{e_icon}{e_match_raw}</font>", body_text)
                    ])

                    e_parenthetical = c_data.get("exhibit_parenthetical")
                    exh_rows.append([
                        Paragraph("Exhibit Index Parenthetical", body_text),
                        Paragraph(e_parenthetical if e_parenthetical else "<font color='#8B0000'>✘ Missing</font>", body_text),
                        Paragraph("-", body_text), Paragraph("-", body_text),
                        Paragraph("<font color='#228B22'>✔ Exact Match</font>" if e_parenthetical else "<font color='#DC143C'>✘ No Match</font>", body_text)
                    ])

                    exh_items = c_data.get("exhibits_page_numbers") or []
                    if not exh_items:
                        exh_rows.append([
                            Paragraph("Exhibit Page", body_text), 
                            Paragraph("<font color='#FF8C00'>Retained/None marked.</font>", body_text), 
                            Paragraph("<font color='#228B22'>N/A</font>", body_text), 
                            Paragraph("<font color='#228B22'>N/A</font>", body_text), 
                            Paragraph("<font color='#228B22'>✔ Exact Match</font>", body_text)
                        ])
                    else:
                        for exh in exh_items:
                            ex_p = str(exh.get('page', ''))
                            exhibit_name = exh.get('name', '')
                            
                            def normalize(s):
                                return "".join(char for char in str(s).lower() if char.isalnum())

                            clean_exh_name = normalize(exhibit_name)
                            exhibit_comparison_raw = "Missing"

                            for key, status in exh_result.items():
                                clean_key = normalize(key)
                                if clean_exh_name in clean_key or clean_key in clean_exh_name:
                                    exhibit_comparison_raw = status
                                    break
                            
                            if c_data.get("index_to_exhibits_retained"):
                                file_status = "-"
                                f_col, f_icon = "black", ""
                            else:
                                if any(match in str(exhibit_comparison_raw) for match in ["Found", "Exact Match"]):
                                    file_status = "Found"
                                    f_col, f_icon = "#228B22", "✔ "
                                elif "1/1" in str(c_data.get("exhibit_file_count", "")):
                                    file_status = "Found"
                                    f_col, f_icon = "#228B22", "✔ "
                                else:
                                    file_status = "Missing"
                                    f_col, f_icon = "#8B0000", "✘ "
                            
                            exh_rows.append([
                                Paragraph("Exhibit Page", body_text),
                                Paragraph(f"{exhibit_name}", body_text),
                                Paragraph(f"<font color='{f_col}'>{f_icon}{file_status}</font>", body_text),
                                Paragraph(ex_p, body_text),
                                Paragraph("<font color='#228B22'>✔ Exact Match</font>", body_text)
                            ])

                    add_exhibits = c_data.get("additional_exhibits_found", [])
                    if not add_exhibits:
                        exh_rows.append([
                            Paragraph("Additional Exhibits Found?", body_text), 
                            Paragraph("<font color='#228B22'>None</font>", body_text), 
                            Paragraph("<font color='#228B22'>N/A</font>", body_text), 
                            Paragraph("<font color='#228B22'>N/A</font>", body_text), 
                            Paragraph("<font color='#228B22'>✔ Exact Match</font>", body_text)
                        ])
                    else:
                        for exh in add_exhibits:
                            exh_rows.append([
                                Paragraph("Additional Exhibits Found?", body_text),
                                Paragraph(f"<font color='#8B0000'>{exh.get('text', '✘ Missing')}</font>", body_text),
                                Paragraph(f"<font color='#8B0000'>{exh.get('file', '✘ Missing')}</font>", body_text),
                                Paragraph(f"<font color='#8B0000'>{exh.get('page', '✘ Missing')}</font>", body_text),
                                Paragraph("<font color='#8B0000'>✘ Missing</font>", body_text)
                            ])

                    t_exh = Table(exh_rows, colWidths=[1.3*inch, 2.3*inch, 0.8*inch, 0.8*inch, 1.3*inch])
                    t_exh.setStyle(table_style)
                    elements.append(t_exh)
                    continue 

                elements.append(Paragraph(sec_name, section_head_style))
                
                if sec_name == "Body Details":
                    headers = [Paragraph("Element", head_text), Paragraph("Transcript", head_text), Paragraph("Notice", head_text), Paragraph("RB", head_text), Paragraph("Title Page", head_text)]
                    col_widths = [1.2*inch, 2.3*inch, 1.15*inch, 1.15*inch, 1.15*inch]
                    active_dicts = [(n_res, active_notice_exc), (rb_res, RB_EXCEPTIONS), (tp_res, [])]
                elif sec_name == "Closing Details":
                    headers = [Paragraph("Element", head_text), Paragraph("Transcript", head_text), Paragraph("RB", head_text)]
                    col_widths = [1.4*inch, 3.3*inch, 1.4*inch, 1.4*inch]
                    active_dicts = [(rb_res, RB_EXCEPTIONS)]
                else:
                    headers = [Paragraph("Element", head_text), Paragraph("Transcript", head_text), Paragraph("Notice", head_text), Paragraph("RB", head_text)]
                    col_widths = [1.4*inch, 3.3*inch, 1.4*inch, 1.4*inch]
                    active_dicts = [(n_res, active_notice_exc), (rb_res, RB_EXCEPTIONS)]

                rows = [headers]
                
                for f in fields:
                    base_f = f.replace('_1', '').replace('_2', '').replace('_cont', '')
                    raw_val = c_data.get(f) if c_data.get(f) is not None else c_data.get(f"transcript_{f}")
                    
                    # --- NEW CLEANING LOGIC START ---
                    # Check if the value is a list (like in Appearances Cont.)
                    if isinstance(raw_val, list):
                        # Join with <br/> for ReportLab line breaks and remove bracket artifacts
                        t_val = "<br/>".join(str(item) for item in raw_val)
                    else:
                        t_val = str(raw_val)
                    
                    val_str_lower = t_val.strip().lower()
                    # --- NEW CLEANING LOGIC END ---

                    is_special = base_f in ["certificate_date", "disclosure_date"]
                    is_missing = raw_val in [None, "", "Missing"] or val_str_lower == "missing" or not val_str_lower

                    if is_special and is_missing:
                        display_val, t_color = "✘ Missing", "#8B0000"
                    elif is_missing:
                        display_val, t_color = "✘ Missing", "#8B0000"
                    else:
                        display_val, t_color = t_val, "black"

                    row_content = [Paragraph(format_label(f), body_text), Paragraph(f"<font color='{t_color}'>{display_val}</font>", body_text)]
                    
                    for res_dict, exc_list in active_dicts:
                        if f in exc_list or base_f in exc_list or base_f in ["duly_sworn", "signature_status", "end_time"]:
                            row_content.append(Paragraph("-", body_text))
                            continue
                        
                        m_raw = res_dict.get(f) if res_dict.get(f) is not None else res_dict.get(f"{f}_match")
                        m_col, m_icon = get_status_info(m_raw)
                        m_label = str(m_raw) if m_raw else "Missing"
                        
                        if m_label == "No Match": m_col = "#DC143C"
                        
                        if is_special and (m_label.lower() == "missing" or not m_raw):
                            m_label, m_col, m_icon = "None", colors.black, ""
                        elif m_label.lower() == "missing":
                            m_col, m_icon = colors.black, "" 
                            
                        row_content.append(Paragraph(f"<font color='{m_col}'>{m_icon}{m_label}</font>", body_text))

                    rows.append(row_content)
                    
                t = Table(rows, colWidths=col_widths)
                t.setStyle(table_style)
                elements.append(t)

            if idx < len(combined_results) - 1: elements.append(PageBreak())

        doc.build(elements)
        return pdf_path
    except Exception as e:
        print(f"PDF Error: {e}")
        raise e

def createReportPDF(jobNo, folder_path, results_list):
    pdf_path = create_multi_page_report(jobNo, folder_path, results_list)
    first_iter = results_list[0]
    is_fla = first_iter.get('isFlorida', False)
    target_sections = SECTIONS_FLORIDA if is_fla else SECTIONS
    current_fields_list = [f for sec in target_sections for f in sec[1]]
    active_notice_exc = NOTICE_EXCEPTIONS if first_iter.get('hasMatchingNotice', False) else OTHER_NOTICE_EXCEPTIONS
    
    notice_summary = calculate_stats(first_iter.get('notice_comparison_result', {}), current_fields_list, active_notice_exc, first_iter.get('combined_data'))
    rb_summary = calculate_stats(first_iter.get('rb_comparison_result', {}), current_fields_list, RB_EXCEPTIONS, first_iter.get('combined_data'))
    
    return pdf_path, f"{first_iter.get('txt_file_name')} | {first_iter.get('doc_file_name')}", notice_summary, rb_summary, len(results_list) - 1