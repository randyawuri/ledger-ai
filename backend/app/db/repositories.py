from typing import Any

from sqlalchemy.orm import Session


class BaseRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(self, entity: Any):
        self.db.add(entity)

    def save(self, entity: Any):
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def refresh(self, entity: Any):
        self.db.refresh(entity)

    def flush(self):
        self.db.flush()

    def delete_entity(self, entity: Any):
        self.db.delete(entity)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()