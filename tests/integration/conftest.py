"""Integration test setup: the real app talking to a real, throwaway Postgres.

Safety: these tests wipe every table before each test. They only run when
RUN_INTEGRATION_TESTS=1 is set AND the database host is local, so they can
never be pointed at the production (Neon) database by accident.
Migrations must already be applied (CI runs `python -m app.migrate` first).
"""
import os
from urllib.parse import urlparse

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.config import settings

from app.db.session import engine
from app.main import app

SAFE_HOSTS = {"localhost", "127.0.0.1", "postgres", "db"}

if os.environ.get("RUN_INTEGRATION_TESTS") != "1":
    # Not opted in: don't even collect the integration tests
    collect_ignore_glob = ["test_*.py"]
elif urlparse(settings.DATABASE_URL).hostname not in SAFE_HOSTS:
    raise pytest.UsageError(
        f"Refusing to run integration tests against non-local database host "
        f"{urlparse(settings.DATABASE_URL).hostname!r}"
    )


@pytest.fixture(autouse=True)
async def clean_database():
    """Every test starts with empty tables."""
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE tracking_events, parcels, partners, users RESTART IDENTITY CASCADE")
        )
    yield
    # Drop pooled connections: each test runs in its own event loop
    await engine.dispose()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


ADMIN = {"full_name": "Ada Admin", "email": "admin@example.com", "password": "admin-pass", "role": "admin"}


async def login(client: AsyncClient, email: str, password: str) -> dict:
    response = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
async def admin_headers(client):
    """Bootstraps the first (admin) user and returns auth headers for them."""
    assert (await client.post("/api/v1/auth/signup", json=ADMIN)).status_code == 200
    return await login(client, ADMIN["email"], ADMIN["password"])


RIDER = {"full_name": "Rex Rider", "email": "rex@example.com", "password": "rider-pass", "role": "rider"}


@pytest.fixture
async def rider(client, admin_headers):
    """Creates a rider; returns (rider_id, rider_auth_headers)."""
    created = await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    assert created.status_code == 200, created.text
    return created.json()["id"], await login(client, RIDER["email"], RIDER["password"])


@pytest.fixture
async def speedaf(client, admin_headers):
    """The partner that SPD-prefixed waybills map to."""
    created = await client.post("/api/v1/partners/", json={"name": "Speedaf"}, headers=admin_headers)
    assert created.status_code == 200, created.text
    return created.json()["id"]


async def make_overdue(waybill: str) -> None:
    """Moves a parcel's delivery deadline into the past (simulates 5+ days passing)."""
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE parcels SET delivery_deadline = now() - interval '1 day' WHERE waybill_number = :w"),
            {"w": waybill},
        )
