from app.memory.conversation.service import conversation


class ContextBuilder:
    def build(self, message: str):
        history = conversation.history()

        history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        return history


context_builder = ContextBuilder()
