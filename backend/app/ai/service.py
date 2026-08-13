from app.ai.client import AIClient
from app.ai.context import ContextBuilder
from app.ai.prompts import SYSTEM_PROMPT


class AIService:

    def __init__(self, db):
        self.db = db
        self.client = AIClient()
        self.context_builder = ContextBuilder(db)

    def chat(self, user, message: str):

        context = self.context_builder.build(user)

        prompt = f"""
Financial Context

{context}

User Question

{message}
"""

        answer = self.client.ask(
            SYSTEM_PROMPT,
            prompt,
        )

        return {
            "response": answer,
        }