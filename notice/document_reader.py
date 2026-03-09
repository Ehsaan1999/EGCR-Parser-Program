import os
from notice.pdf_reader import PDFReader
from notice.word_reader import WordReader


class DocumentReader:
    """
    Factory class that selects the correct reader
    based on file extension.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.reader = self._get_reader()

    def _get_reader(self):
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".pdf":
            return PDFReader(self.file_path)

        if ext == ".docx":
            return WordReader(self.file_path)

        raise ValueError(f"Unsupported file type: {ext}")

    def read(self) -> str:
        return self.reader.read()

if __name__ == "__main__":
    doc_reader = DocumentReader("./test_files/legal docs/6/2025.02.27-Lt.-Humphrey-depo-notice.docx")
    content = doc_reader.read()
    print(content)
