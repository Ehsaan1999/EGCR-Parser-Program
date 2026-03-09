from docx import Document
from .base_reader import BaseReader


class WordReader(BaseReader):
    """
    Reads text from Word (.docx) files.
    """

    def read(self) -> str:
        document = Document(self.file_path)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
