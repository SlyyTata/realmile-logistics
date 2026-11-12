"""Logistics partners stored in and read back from the database."""


async def test_create_and_list_partners(client, admin_headers):
    created = await client.post(
        "/api/v1/partners/", json={"name": "Speedaf", "contact_phone": "0800"}, headers=admin_headers
    )
    assert created.status_code == 200
    assert created.json()["name"] == "Speedaf"

    listed = await client.get("/api/v1/partners/", headers=admin_headers)
    assert [p["name"] for p in listed.json()] == ["Speedaf"]


async def test_duplicate_partner_is_rejected(client, admin_headers):
    await client.post("/api/v1/partners/", json={"name": "GIG"}, headers=admin_headers)
    response = await client.post("/api/v1/partners/", json={"name": "GIG"}, headers=admin_headers)
    assert response.status_code == 400
