from datetime import datetime
from pathlib import Path

# Change this later to your configurable vault location
VAULT_PATH = Path.home() / "Documents" / "Obsidian"

CONVERSATION_DIR = VAULT_PATH / "conversation"


class ConversationWriter:
    def _today_file(self) -> Path:
        now = datetime.now()

        folder = (
            CONVERSATION_DIR
            / str(now.year)
            / f"{now.month:02d}"
        )

        folder.mkdir(parents=True, exist_ok=True)

        return folder / f"{now.date()}.md"

    def append(
        self,
        role: str,
        content: str,
    ) -> None:

        now = datetime.now()

        file = self._today_file()

        with open(file, "a", encoding="utf-8") as f:
            f.write(
                f"\n## {now.strftime('%H:%M:%S')}\n\n"
            )
            f.write(f"**{role.title()}**\n\n")
            f.write(content)
            f.write("\n\n---\n")


conversation_writer = ConversationWriter()
