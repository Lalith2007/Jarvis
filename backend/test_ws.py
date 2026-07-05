import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws/platform"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            await websocket.send("Hello")
            print("Sent Hello")
    except Exception as e:
        print(f"Failed to connect: {e}")

asyncio.run(test())
