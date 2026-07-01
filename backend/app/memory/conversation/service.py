from app.memory.conversation.models import Message


class ConversationService:
    def __init__(self):
        self.messages = []

    def add_user(self, message: str):
        self.messages.append(
            Message(
                role="user",
                content=message,
            )
        )

    def add_assistant(self, message: str):
        self.messages.append(
            Message(
                role="assistant",
                content=message,
            )
        )

    def history(self):
        return [
            {
                "role": m.role,
                "content": m.content,
            }
            for m in self.messages
        ]

    def clear(self):
        self.messages = []


conversation = ConversationService()
