import os
from typing import List, Dict, Any
from utils.create_file_combinations import create_file_combinations
from main import process_documents
from report.report_generator import createReportPDF

class DocumentProcessor:
    def __init__(self, folder_path: str, progress_callback=None):
        self.folder_path = folder_path
        self.progress_callback = progress_callback

    def process(self):
        """
        Processes all valid TXT + Notice combinations.
        Extracts data first, then generates ONE PDF.
        Returns final PDF path.
        """
        jobNo = ""
        combinations = create_file_combinations(self.folder_path)
        jobNo = combinations[0].get("jobNo", "")
        if not combinations:
            raise RuntimeError("No valid TXT / Notice combinations found.")

        total = len(combinations)
        extracted_payloads: List[Dict[str, Any]] = []
        errors = []

        for idx, item in enumerate(combinations, start=1):
            txt_name = os.path.basename(item["txt_path"])

            # 🔔 Notify UI about progress + filename
            if self.progress_callback:
                self.progress_callback(
                    current=idx,
                    total=total,
                    filename=txt_name
                )

            print(f"\n🚀 Processing document {idx}/{total} — {txt_name}")

            try:
                payload = process_documents(
                    TEXT_FOLDER=os.path.dirname(item["txt_path"]),
                    FILENAME=txt_name,
                    NOTICE_FILENAME=os.path.basename(item["notice_path"]),
                    jobNo=item["jobNo"],
                    hasMatchingNotice=item["hasMatchingNotice"],
                    progress_callback=self.progress_callback
                )

                if payload:
                    extracted_payloads.append(payload)

            except Exception as e:
                errors.append(f'{item["txt_path"]}: {e}')
                print(f"❌ Error: {e}")

        if not extracted_payloads:
            raise RuntimeError(
                f"No documents processed successfully. Errors: {errors}"
            )

        # --------------------------------------------------
        # Generate PDF ONCE using all extracted data
        # --------------------------------------------------
        final_pdf_path, input_file_name, notice_summary, rb_summary, plusCount = createReportPDF(
            jobNo=jobNo,
            folder_path=str(self.folder_path),
            results_list=extracted_payloads
        )

        if not final_pdf_path or not os.path.exists(final_pdf_path):
            raise RuntimeError("PDF generation failed.")

        return final_pdf_path, input_file_name, notice_summary, rb_summary, plusCount
