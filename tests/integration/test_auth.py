"""Signup lockdown and login, end to end through HTTP and the database."""
from tests.integration.conftest import ADMIN, login


async def test_first_signup_is_always_admin(client):
    # Even if the caller asks to be a rider, the bootstrap user becomes admin
    response = await client.post("/api/v1/auth/signup", json={**ADMIN, "role": "rider"})
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "admin"
    assert "password" not in body and "hashed_password" not in body


async def test_signup_closes_after_first_user(client, admin_headers):
    response = await client.post(
        "/api/v1/auth/signup",
        json={"full_name": "Eve", "email": "eve@example.com", "password": "pw", "role": "admin"},
    )
    assert response.status_code == 403


async def test_login_returns_working_token(client, admin_headers):
    me = await client.get("/api/v1/users/me", headers=admin_headers)
    assert me.status_code == 200
    assert me.json()["email"] == ADMIN["email"]


async def test_login_rejects_wrong_password(client, admin_headers):
    response = await client.post(
        "/api/v1/auth/login", data={"username": ADMIN["email"], "password": "wrong"}
    )
    assert response.status_code == 401


async def test_login_rejects_unknown_user(client):
    response = await client.post(
        "/api/v1/auth/login", data={"username": "nobody@example.com", "password": "pw"}
    )
    assert response.status_code == 401


async def test_token_for_deleted_user_stops_working(client, admin_headers):
    rider = {"full_name": "Rex", "email": "rex@example.com", "password": "rider-pass", "role": "rider"}
    created = await client.post("/api/v1/users/", json=rider, headers=admin_headers)
    rider_headers = await login(client, rider["email"], rider["password"])

    deleted = await client.delete(f"/api/v1/users/{created.json()['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert (await client.get("/api/v1/users/me", headers=rider_headers)).status_code == 401
