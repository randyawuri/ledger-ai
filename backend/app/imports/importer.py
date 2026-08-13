from sqlalchemy.orm import Session

from app.imports.detector import detect_parser
from app.imports.schemas import ImportedTransaction


class Importer:
    """
    Responsible only for parsing statement files.
    """

    def __init__(self, db: Session):
        self.db = db

    def import_file(
        self,
        file_path: str,
    ) -> list[ImportedTransaction]:

        parser = detect_parser(file_path)

        return parser.parse(file_path)