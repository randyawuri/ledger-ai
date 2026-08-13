from openai import OpenAI

from app.core.config import settings


class AIClient:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
        )

    def ask(self, system_prompt: str, user_prompt: str) -> str:

        response = self.client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.output_text