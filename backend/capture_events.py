import asyncio
import httpx
import websockets
import json

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/platform"

async def capture():
    # Stream request
    print("--- 8. STREAMING VALIDATION ---")
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", 
            f"{BASE_URL}/api/chat/stream", 
            json={"message": "Hello, briefly.", "session_id": "test-cert"}
        ) as response:
            count = 0
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "): continue
                print(line)
                count += 1
                if count >= 3:
                    print("... (truncated for brevity) ...")
                    break

    # WS request
    print("\n--- 9. WEBSOCKET VALIDATION ---")
    async with websockets.connect(WS_URL) as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print("Received WS Message:", msg)
        print("\n--- 6. EVENT VALIDATION ---")
        event = json.loads(msg)
        print(json.dumps(event, indent=2))
        
if __name__ == "__main__":
    asyncio.run(capture())
