"""Admin-only user management and role-based access."""
from tests.integration.conftest import RIDER, login


async def test_ops_staff_can_view_team_lists(client, admin_headers):
    ops = {**RIDER, "email": "ops@example.com", "role": "ops_staff"}
    await client.post("/api/v1/users/", json=ops, headers=admin_headers)
    ops_headers = await login(client, ops["email"], ops["password"])
    assert (await client.get("/api/v1/users/team/rider", headers=ops_headers)).status_code == 200


async def test_admin_creates_rider_who_can_log_in(client, admin_headers):
    response = await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "rider"

    rider_headers = await login(client, RIDER["email"], RIDER["password"])
    me = await client.get("/api/v1/users/me", headers=rider_headers)
    assert me.json()["email"] == RIDER["email"]


async def test_duplicate_email_is_rejected(client, admin_headers):
    await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    response = await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    assert response.status_code == 400


async def test_rider_cannot_manage_users(client, admin_headers):
    await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    rider_headers = await login(client, RIDER["email"], RIDER["password"])

    assert (await client.get("/api/v1/users/", headers=rider_headers)).status_code == 403
    new_user = {**RIDER, "email": "sneaky@example.com", "role": "admin"}
    assert (await client.post("/api/v1/users/", json=new_user, headers=rider_headers)).status_code == 403


async def test_riders_list_contains_only_delivery_staff(client, admin_headers):
    await client.post("/api/v1/users/", json=RIDER, headers=admin_headers)
    response = await client.get("/api/v1/users/operations/riders", headers=admin_headers)
    assert response.status_code == 200
    assert [u["email"] for u in response.json()] == [RIDER["email"]]


async def test_deleting_missing_user_returns_404(client, admin_headers):
    response = await client.delete("/api/v1/users/9999", headers=admin_headers)
    assert response.status_code == 404


async def test_rider_cannot_delete_users(client, admin_headers, rider):
    rider_id, rider_headers = rider
    response = await client.delete(f"/api/v1/users/{rider_id}", headers=rider_headers)
    assert response.status_code == 403


async def test_team_list_filters_by_role(client, admin_headers, rider):
    response = await client.get("/api/v1/users/team/rider", headers=admin_headers)
    assert response.status_code == 200
    assert [u["email"] for u in response.json()] == [RIDER["email"]]

    admins = await client.get("/api/v1/users/team/admin", headers=admin_headers)
    assert [u["role"] for u in admins.json()] == ["admin"]


async def test_rider_cannot_view_team_lists(client, rider):
    _, rider_headers = rider
    assert (await client.get("/api/v1/users/team/rider", headers=rider_headers)).status_code == 403
