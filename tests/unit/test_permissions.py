"""Role checks and routes that must reject anonymous callers (no database needed)."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.dependencies import check_admin
from app.main import app
from app.models.user import UserRole

client = TestClient(app)


def test_check_admin_allows_admin():
    admin = SimpleNamespace(role=UserRole.ADMIN)
    assert check_admin(admin) is admin


@pytest.mark.parametrize("role", [r for r in UserRole if r is not UserRole.ADMIN])
def test_check_admin_blocks_every_other_role(role):
    with pytest.raises(HTTPException) as exc:
        check_admin(SimpleNamespace(role=role))
    assert exc.value.status_code == 403


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/v1/users/me"),
        ("get", "/api/v1/users/"),
        ("get", "/api/v1/users/operations/riders"),
        ("get", "/api/v1/partners/"),
        ("post", "/api/v1/partners/"),
    ],
)
def test_protected_routes_need_a_token(method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401


def test_garbage_token_is_rejected():
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_docs_are_served_under_api_prefix():
    # The load balancer only forwards /api/* to the API, so docs must live there
    assert client.get("/api/openapi.json").status_code == 200


def test_health_returns_503_when_database_is_unreachable(monkeypatch):
    # Point the health check at a port where nothing listens. The load balancer
    # relies on this 503 to stop sending traffic to a task that lost its database.
    from sqlalchemy.ext.asyncio import create_async_engine

    import app.main

    dead = create_async_engine("postgresql+asyncpg://x:x@127.0.0.1:1/x", connect_args={"ssl": False})
    monkeypatch.setattr(app.main, "engine", dead)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "database": "unreachable"}
