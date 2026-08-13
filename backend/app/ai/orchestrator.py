class AIOrchestrator:

    def __init__(self, db):

        self.context = ContextBuilder(db)

        self.client = AIClient()

    def ask(self, user, question):

        context = self.context.build(user)

        prompt = f"""

Financial Context

{context}

Question

{question}

"""

        return self.client.chat(
            SYSTEM_PROMPT,
            prompt,
        )