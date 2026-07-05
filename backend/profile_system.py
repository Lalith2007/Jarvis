import asyncio
import time
import httpx
import websockets
import json
import statistics

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/platform"

async def profile_system():
    print("Starting Architecture Certification Profiling...")
    results = {}

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/dashboard")
        assert resp.status_code == 200
    results["dashboard_load_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    async with websockets.connect(WS_URL) as ws:
        pass
    results["websocket_connect_ms"] = (time.perf_counter() - start) * 1000

    first_token_latency = []
    total_mission_latency = []
    token_counts = []
    
    async def chat_stream_request(i):
        req_start = time.perf_counter()
        first_token_time = None
        tokens = 0
        timeout = httpx.Timeout(120.0, read=120.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST", 
                f"{BASE_URL}/api/chat/stream", 
                json={"message": "Count to 3 quickly.", "session_id": f"stress-{i}"}
            ) as response:
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "): continue
                    data = json.loads(line[6:])
                    if data["type"] == "chunk":
                        if first_token_time is None:
                            first_token_time = time.perf_counter()
                        tokens += 1
        
        total_time = time.perf_counter() - req_start
        if first_token_time:
            first_token_latency.append((first_token_time - req_start) * 1000)
        total_mission_latency.append(total_time * 1000)
        token_counts.append(tokens)

    # Concurrency test (3 parallel streams to avoid rate limits)
    await asyncio.gather(*(chat_stream_request(i) for i in range(3)))

    results["first_token_avg_ms"] = statistics.mean(first_token_latency) if first_token_latency else 0
    results["total_mission_avg_ms"] = statistics.mean(total_mission_latency) if total_mission_latency else 0
    results["avg_tokens_received"] = statistics.mean(token_counts) if token_counts else 0
    results["average_token_latency_ms"] = (results["total_mission_avg_ms"] - results["first_token_avg_ms"]) / max(1, results["avg_tokens_received"])

    print("\n--- ARCHITECTURE SCORECARD METRICS ---")
    for k, v in results.items():
        print(f"{k}: {v:.2f}")
    
if __name__ == "__main__":
    asyncio.run(profile_system())
