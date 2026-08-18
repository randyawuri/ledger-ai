from abc import ABC
from abc import abstractmethod

from sqlalchemy import func

from app.accounts.domain.models import Account
from app.budgets.domain.models import Budget
from app.transactions.domain.models import Transaction
from app.common.enums import TransactionType


class AutomationRule(ABC):

    @abstractmethod
    def applies(self, db, transaction):
        pass

    @abstractmethod
    def execute(self, db, transaction):
        pass


#
# ----------------------------------------------------
# Large Expense Rule
# ----------------------------------------------------
#

class LargeExpenseRule(AutomationRule):

    LIMIT = 100000

    def applies(self, db, transaction):

        return (
            transaction.transaction_type == TransactionType.DEBIT
            and transaction.amount >= self.LIMIT
        )

    def execute(self, db, transaction):

        return {
            "rule_name": "Large Expense",
            "action": (
                f"Expense of ₦{transaction.amount:,.2f} "
                "was flagged."
            ),
            "payload": {
                "amount": float(transaction.amount),
            },
        }


#
# ----------------------------------------------------
# Salary Rule
# ----------------------------------------------------
#

class SalaryRule(AutomationRule):

    KEYWORDS = [
        "salary",
        "payroll",
        "salary payment",
        "salary credit",
        "monthly salary",
    ]

    def applies(self, db, transaction):

        if transaction.transaction_type != TransactionType.CREDIT:
            return False

        if not transaction.description:
            return False

        description = transaction.description.lower()

        return any(
            keyword in description
            for keyword in self.KEYWORDS
        )

    def execute(self, db, transaction):

        return {
            "rule_name": "Salary Detected",
            "action": "Salary payment detected.",
            "payload": {
                "amount": float(transaction.amount),
            },
        }


#
# ----------------------------------------------------
# Budget Rule
# ----------------------------------------------------
#

class BudgetExceededRule(AutomationRule):

    LIMIT = 80

    def applies(self, db, transaction):

        if (
            transaction.transaction_type
            != TransactionType.DEBIT
        ):
            return False

        if transaction.category_id is None:
            return False

        budget = (
            db.query(Budget)
            .filter(
                Budget.user_id == transaction.account.user_id,
                Budget.category_id == transaction.category_id,
            )
            .first()
        )

        if not budget:
            return False

        spent = (
            db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .join(Account)
            .filter(
                Account.user_id == transaction.account.user_id,
                Transaction.category_id == transaction.category_id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .scalar()
        )

        percent = float(
            spent / budget.amount * 100
        )

        return percent >= self.LIMIT

    def execute(self, db, transaction):

        return {
            "rule_name": "Budget Alert",
            "action": (
                "Budget usage exceeded "
                "80%."
            ),
            "payload": {
                "category_id": str(
                    transaction.category_id
                ),
            },
        }


#
# ----------------------------------------------------
# Low Balance Rule
# ----------------------------------------------------
#

class LowBalanceRule(AutomationRule):

    LIMIT = 10000

    def applies(self, db, transaction):

        account = transaction.account

        income = (
            db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .filter(
                Transaction.account_id == account.id,
                Transaction.transaction_type
                == TransactionType.CREDIT,
            )
            .scalar()
        )

        expenses = (
            db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .filter(
                Transaction.account_id == account.id,
                Transaction.transaction_type
                == TransactionType.DEBIT,
            )
            .scalar()
        )

        balance = (
            account.opening_balance
            + income
            - expenses
        )

        return balance <= self.LIMIT

    def execute(self, db, transaction):

        return {
            "rule_name": "Low Balance",
            "action": (
                "Account balance is low."
            ),
            "payload": {},
        }


#
# ----------------------------------------------------
# Duplicate Transaction Rule
# ----------------------------------------------------
#

class DuplicateTransactionRule(AutomationRule):

    def applies(self, db, transaction):

        duplicates = (
            db.query(Transaction)
            .filter(
                Transaction.account_id == transaction.account_id,
                Transaction.amount == transaction.amount,
                Transaction.description
                == transaction.description,
                Transaction.id != transaction.id,
            )
            .count()
        )

        return duplicates > 0

    def execute(self, db, transaction):

        return {
            "rule_name": "Duplicate Transaction",
            "action": (
                "Possible duplicate detected."
            ),
            "payload": {},
        }