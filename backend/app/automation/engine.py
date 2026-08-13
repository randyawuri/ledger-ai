from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.automation.domain.models import Automation
from app.automation.domain.models import AutomationStatus

from app.automation.rules import (
    BudgetExceededRule,
    DuplicateTransactionRule,
    LargeExpenseRule,
    LowBalanceRule,
    SalaryRule,
)


class AutomationEngine:

    def __init__(self, db: Session):
        self.db = db

        self.rules = [
            SalaryRule(),
            LargeExpenseRule(),
            BudgetExceededRule(),
            LowBalanceRule(),
            DuplicateTransactionRule(),
        ]

    def process(self, transaction):

        executed = []

        for rule in self.rules:

            try:

                if not rule.applies(
                    self.db,
                    transaction,
                ):
                    continue

                result = rule.execute(
                    self.db,
                    transaction,
                )

                automation = Automation(
                    user_id=transaction.account.user_id,
                    transaction_id=transaction.id,
                    rule_name=result["rule_name"],
                    action=result["action"],
                    payload=result.get("payload"),
                    status=AutomationStatus.EXECUTED,
                    executed_at=datetime.now(UTC),
                )

                self.db.add(automation)

                executed.append(automation)

            except Exception as exc:

                failed = Automation(
                    user_id=transaction.account.user_id,
                    transaction_id=transaction.id,
                    rule_name=rule.__class__.__name__,
                    action=str(exc),
                    status=AutomationStatus.FAILED,
                    executed_at=datetime.now(UTC),
                )

                self.db.add(failed)

        self.db.commit()

        return executed