from pydantic import BaseModel


class Insight(BaseModel):
    title: str
    description: str
    severity: str


class InsightsResponse(BaseModel):
    insights: list[Insight]