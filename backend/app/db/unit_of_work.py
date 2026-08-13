from sqlalchemy.orm import Session

from app.accounts.repository import AccountRepository
from app.transactions.repository import TransactionRepository
from app.categories.repository import CategoryRepository
from app.budgets.repository import BudgetRepository
from app.merchants.repository import MerchantRepository
from app.automation.repository import AutomationRepository
from app.goals.repository import GoalRepository


class UnitOfWork:

    def __init__(self, db: Session):

        self.db = db

        self.accounts = AccountRepository(db)
        self.transactions = TransactionRepository(db)
        self.categories = CategoryRepository(db)
        self.budgets = BudgetRepository(db)
        self.merchants = MerchantRepository(db)
        self.automations = AutomationRepository(db)
        self.goals = GoalRepository(db)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()