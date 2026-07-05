import asyncio
import sys
from app.agents.hermes.service import hermes
from app.config.settings import settings

def test():
    print(f"Base URL: {settings.BASE_URL}")
    print(f"Default Model: {settings.DEFAULT_MODEL}")
    try:
        for chunk in hermes.chat_stream("Which model are you?"):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"Error: {e}")

test()
