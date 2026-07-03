import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
    "Content-Type": "application/json",
}

payload = {
    "model": "openai/gpt-oss-20b",
    "messages": [
        {
            "role": "user",
            "content": "Reply only with OK."
        }
    ],
    "max_tokens": 5,
}

print("Sending request...")

with httpx.Client(timeout=30.0) as client:
    response = client.post(
        url,
        headers=headers,
        json=payload,
    )

print(response.status_code)
print(json.dumps(response.json(), indent=2))
