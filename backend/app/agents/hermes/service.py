from app.llm.service import llm
from app.memory.conversation.service import conversation


class Hermes:
    def __init__(self):
        self.llm = llm
        self.conversation = conversation

    def chat(self, message: str) -> str:
        # Save the user's message
        self.conversation.add_user(message)

        # Send the full conversation history to the LLM
        response = self.llm.chat(
            self.conversation.history()
        )

        # Save the assistant's reply
        self.conversation.add_assistant(response)

        return response


hermes = Hermes()
