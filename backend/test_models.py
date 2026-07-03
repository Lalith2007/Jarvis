import os
import httpx
from dotenv import load_dotenv

load_dotenv()

response = httpx.get(
    "https://integrate.api.nvidia.com/v1/models",
    headers={
        "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}"
    },
    timeout=30,
)

print(response.status_code)
print(response.text)
