"""
API surface tests using FastAPI TestClient.

Covers the app boot, the root endpoint, and the optional token-auth middleware
(enforced only when JARVIS_API_TOKEN is set).
"""
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    import main
    return TestClient(main.app)


def test_root_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_no_auth_required_when_token_unset(monkeypatch, client):
    # Default/dev: no JARVIS_API_TOKEN -> /api open (a read-only capabilities
    # route should not 401).
    monkeypatch.delenv("JARVIS_API_TOKEN", raising=False)
    resp = client.get("/api/capabilities")
    assert resp.status_code != 401


def test_auth_enforced_when_token_set(monkeypatch):
    monkeypatch.setenv("JARVIS_API_TOKEN", "s3cret")
    import main
    importlib.reload(main)  # not required for env read, but keeps app fresh
    c = TestClient(main.app)

    # Missing/incorrect token -> 401 on /api routes.
    assert c.get("/api/capabilities").status_code == 401
    assert c.get(
        "/api/capabilities", headers={"Authorization": "Bearer wrong"}
    ).status_code == 401

    # Correct token -> not 401.
    ok = c.get("/api/capabilities", headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code != 401

    # X-API-Token header also accepted.
    ok2 = c.get("/api/capabilities", headers={"X-API-Token": "s3cret"})
    assert ok2.status_code != 401

    # Root (non-/api) is never gated.
    assert c.get("/").status_code == 200


def test_security_manager_filesystem_resource_gate():
    """Granted FILESYSTEM policy still denies paths outside the sandbox."""
    from app.runtime.security import security_manager
    from app.capabilities.models import CapabilityType
    from app.runtime.models import SecurityAction

    assert security_manager.validate_permission(
        CapabilityType.FILESYSTEM, SecurityAction.READ, resource="/etc/passwd"
    ) is False
