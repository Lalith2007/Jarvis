from datetime import datetime

from app.storage.models import StorageObject
from app.storage.service import storage


class ConversationRecorder:
    def record(
        self,
        user: str,
        assistant: str,
    ) -> None:

        now = datetime.now()

        folder = (
            f"jarvis/conversations/"
            f"{now.year}/"
            f"{now.month:02d}"
        )

        filename = f"{now.date()}.md"

        entry = f"""
## {now.strftime("%H:%M:%S")}

### User

{user}

### Assistant

{assistant}

---

"""

        relative_path = f"{folder}/{filename}"

        try:
            existing = storage.read(relative_path)
        except FileNotFoundError:
            existing = "# JARVIS Conversation\n"

        storage.save(
            StorageObject(
                folder=folder,
                filename=filename,
                content=existing + entry,
            )
        )


conversation_recorder = ConversationRecorder()
