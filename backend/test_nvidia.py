from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
)

MODELS = [
    "meta/llama-3.3-70b-instruct",
    "deepseek-ai/deepseek-v4-pro",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "minimaxai/minimax-m3",
]

for model in MODELS:
    print("=" * 60)
    print(model)

    try:
        start = time.time()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Reply ONLY with OK."
                }
            ],
            timeout=30,
        )

        elapsed = time.time() - start

        print("✅", response.choices[0].message.content)
        print(f"{elapsed:.2f} seconds")

    except Exception as e:
        print("❌", e)
