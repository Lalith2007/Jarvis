from pathlib import Path
from dotenv import load_dotenv
import os

# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Load backend/.env
load_dotenv(BASE_DIR / ".env")


class Settings:
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL = os.getenv("MODEL")
    OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT")


settings = Settings()
