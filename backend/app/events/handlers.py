from app.automation.service import AutomationService


class AutomationHandler:

    def __init__(self, db):

        self.db = db

    def __call__(self, event):

        AutomationService(
            self.db
        ).process_transaction(
            event.transaction
        )