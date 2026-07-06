from datetime import datetime
from pathlib import Path

from app.config.settings import settings


class ConversationWriter:
    """Writes conversation logs into the configured vault (no hardcoded paths)."""

    def _vault_root(self) -> Path:
        if not settings.VAULT_PATH:
            raise RuntimeError(
                "No vault configured — set OBSIDIAN_VAULT/VAULT_PATH to write conversations."
            )
        return Path(settings.VAULT_PATH)

    def _today_file(self) -> Path:
        now = datetime.now()
        folder = (
            self._vault_root()
            / "jarvis"
            / "conversations"
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
