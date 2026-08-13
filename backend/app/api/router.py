from fastapi import APIRouter

from app.auth.api.routes import router as auth_router
from app.dashboard.api.routes import (
    router as dashboard_router,
)
from app.accounts.api.routes import router as accounts_router
from app.transactions.api.routes import router as transactions_router
from app.categories.api.routes import router as categories_router
from app.budgets.api.routes import router as budgets_router
from app.goals.api.routes import router as goals_router
from app.analytics.api.routes import router as analytics_router
from app.forecasting.api.routes import router as forecasting_router
from app.health.api.routes import router as health_router
from app.insights.api.routes import router as insights_router
from app.imports.api.routes import router as imports_router

api_router = APIRouter()

api_router.include_router(auth_router)

api_router.include_router(accounts_router)
api_router.include_router(categories_router)
api_router.include_router(transactions_router)
api_router.include_router(budgets_router)
api_router.include_router(goals_router)

api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(forecasting_router)
api_router.include_router(health_router)
api_router.include_router(insights_router)

api_router.include_router(imports_router)