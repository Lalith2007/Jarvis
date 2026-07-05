from pathlib import Path
import os

from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Load backend/.env
load_dotenv(BASE_DIR / ".env")


class Settings:
    # NVIDIA / LLM
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

    # Obsidian
    OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT")
    
    # Athena
    ATHENA_CONFIDENCE_THRESHOLD = float(os.getenv("ATHENA_CONFIDENCE_THRESHOLD", "0.80"))


settings = Settings()
