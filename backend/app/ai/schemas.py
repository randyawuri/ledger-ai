from pydantic import BaseModel


class AIRequest(BaseModel):
    question: str


class AIResponse(BaseModel):
    answer: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str