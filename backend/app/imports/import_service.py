from sqlalchemy.orm import Session

from app.imports.commit_service import CommitService
from app.imports.importer import Importer


class ImportService:
    """
    Application service responsible for orchestrating
    the transaction import workflow.

    Responsibilities:
    - Preview uploaded statements
    - Commit validated transactions
    - Coordinate the import pipeline
    """

    def __init__(self, db: Session):
        self.db = db
        self.importer = Importer(db)
        self.commit_service = CommitService(db)

    def preview(self, file_path: str):
        """
        Parse a statement and return transactions for preview.
        Nothing is persisted.
        """
        return self.importer.import_file(file_path)

    def commit(self, transactions):
        """
        Persist approved transactions.
        """
        return self.commit_service.commit(transactions)