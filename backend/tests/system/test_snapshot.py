from fastapi.testclient import TestClient

from main import app


def test_system_snapshot_returns_live_host_metrics():
    client = TestClient(app)

    response = client.get("/system/snapshot")

    assert response.status_code == 200
    payload = response.json()
    assert payload["hostname"]
    assert payload["uptime_seconds"] >= 0
    assert {metric["key"] for metric in payload["metrics"]} == {
        "cpu",
        "gpu",
        "memory",
        "storage",
        "network",
    }
    assert payload["memory"]["total_bytes"] > 0
    assert payload["storage"]["total_bytes"] > 0
    assert "name" in payload["gpu"]
    assert isinstance(payload["top_processes"], list)
