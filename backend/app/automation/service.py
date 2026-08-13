from sqlalchemy.orm import Session

from app.automation.domain.models import Automation
from app.automation.engine import AutomationEngine


class AutomationService:

    def __init__(self, db: Session):
        self.db = db
        self.engine = AutomationEngine(db)

    def process_transaction(self, transaction):
        """
        Execute all automation rules for a newly
        created transaction.
        """
        return self.engine.process(transaction)

    def list_automations(self, user):
        """
        Return all automation events for a user,
        newest first.
        """
        return (
            self.db.query(Automation)
            .filter(
                Automation.user_id == user.id,
            )
            .order_by(
                Automation.created_at.desc(),
            )
            .all()
        )

    def get_automation(self, automation_id):

        return (
            self.db.query(Automation)
            .filter(
                Automation.id == automation_id,
            )
            .first()
        )

    def rerun_transaction(self, transaction):

        return self.engine.process(transaction)

    def delete_automation(self, automation):

        self.db.delete(automation)
        self.db.commit()

        return {
            "message": "Automation deleted."
        }