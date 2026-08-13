from pydantic import BaseModel


class FinancialHealthResponse(BaseModel):
    score: int
    grade: str
    savings_rate: float
    budget_score: float
    cash_flow_score: float
    spending_score: float
    emergency_score: float
    summary: str