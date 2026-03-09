from abc import ABC, abstractmethod


class BaseReader(ABC):
    """
    Abstract base class for document readers.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def read(self) -> str:
        """
        Read the document and return extracted text.
        """
        pass
