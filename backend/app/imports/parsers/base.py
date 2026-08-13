from abc import ABC, abstractmethod

from app.imports.schemas import ImportedTransaction


class StatementParser(ABC):

    @abstractmethod
    def can_parse(self, headers: list[str]) -> bool:
        ...

    @abstractmethod
    def parse(
        self,
        file_path: str,
    ) -> list[ImportedTransaction]:
        ...