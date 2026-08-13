from uuid import UUID

from sqlalchemy.orm import Session

from app.automation.domain.models import Automation


class AutomationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, automation: Automation):
        self.db.add(automation)
        return automation

    def get(self, automation_id: UUID):
        return (
            self.db.query(Automation)
            .filter(Automation.id == automation_id)
            .first()
        )

    def list_by_user(self, user_id: UUID):
        return (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id)
            .all()
        )

    def active_rules(self, user_id: UUID):
        return (
            self.db.query(Automation)
            .filter(
                Automation.user_id == user_id,
                Automation.enabled.is_(True),
            )
            .all()
        )

    def delete(self, automation: Automation):
        self.db.delete(automation)