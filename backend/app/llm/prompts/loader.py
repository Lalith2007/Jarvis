from pathlib import Path


class PromptLoader:
    def __init__(self):
        self.prompt_dir = Path(__file__).resolve().parent

    def load(self, filename: str) -> str:
        path = self.prompt_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {filename}")

        return path.read_text(encoding="utf-8")


prompt_loader = PromptLoader()
