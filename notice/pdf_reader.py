import pypdf
from .base_reader import BaseReader

class PDFReader(BaseReader):
    """
    Reads text from PDF files.
    """

    def read(self) -> str:
        reader = pypdf.PdfReader(self.file_path)
        text_blocks = []

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_blocks.append(page_text)

        return "\n\n".join(text_blocks)
