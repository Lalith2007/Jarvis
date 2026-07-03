from datetime import datetime


class MarkdownFormatter:
    def conversation(
        self,
        user: str,
        assistant: str,
    ) -> str:

        now = datetime.now()

        return f"""
## {now.strftime("%H:%M:%S")}

### User

{user}

### Assistant

{assistant}

---

"""


markdown = MarkdownFormatter()
