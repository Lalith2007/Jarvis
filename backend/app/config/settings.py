import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Load backend/.env
load_dotenv(BASE_DIR / ".env")


class Settings:
    # NVIDIA / LLM
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

    # Obsidian vault. VAULT_PATH is the canonical name; OBSIDIAN_VAULT is kept
    # as an alias for backward compatibility. Both resolve to the same value.
    OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT") or os.getenv("VAULT_PATH")
    VAULT_PATH = os.getenv("VAULT_PATH") or os.getenv("OBSIDIAN_VAULT")

    # Optional API auth token (see main.py optional_token_auth middleware)
    API_TOKEN = os.getenv("JARVIS_API_TOKEN")

    # Athena
    ATHENA_CONFIDENCE_THRESHOLD = float(os.getenv("ATHENA_CONFIDENCE_THRESHOLD", "0.80"))

    # LLM request bounds — prevent a slow/stuck provider from hanging forever.
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))

    @classmethod
    def validate(cls) -> None:
        """
        Fail-fast validation of required configuration. Call at application
        startup so a misconfigured deployment errors clearly instead of failing
        cryptically on the first LLM call.
        """
        missing = [name for name in ("NVIDIA_API_KEY",) if not getattr(cls, name)]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: "
                + ", ".join(missing)
                + ". Set them in backend/.env or the process environment."
            )
        if not cls.VAULT_PATH:
            logger.warning(
                "No OBSIDIAN_VAULT/VAULT_PATH configured — vault-backed features "
                "(memory, documents) will be unavailable."
            )


settings = Settings()
