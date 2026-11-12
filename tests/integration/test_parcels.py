"""Parcel lifecycle: scan in -> dispatch -> status updates, plus SLA tracking."""
from datetime import datetime, timedelta

from tests.integration.conftest import RIDER, login, make_overdue

WAYBILL = "SPD12345678"


async def scan(client, headers, waybill=WAYBILL):
    return await client.post("/api/v1/parcels/scan-in", json={"waybill_number": waybill}, headers=headers)


async def get_parcel(client, headers, waybill=WAYBILL):
    parcels = (await client.get("/api/v1/parcels/", headers=headers)).json()
    return next(p for p in parcels if p["waybill_number"] == waybill)


async def test_scan_in_detects_partner_and_records_history(client, admin_headers, speedaf):
    response = await scan(client, admin_headers)
    assert response.status_code == 200, response.text
    parcel = response.json()

    assert parcel["partner_id"] == speedaf
    assert parcel["status"] == "in_warehouse"
    assert parcel["rider_id"] is None
    assert parcel["recipient_name"] == f"Recipient for {WAYBILL}"
    assert parcel["recipient_phone"] == "08012345678"
    assert [e["status"] for e in parcel["history"]] == ["in_warehouse"]

    # 5-day delivery SLA starts at scan-in
    deadline = datetime.fromisoformat(parcel["delivery_deadline"])
    created = datetime.fromisoformat(parcel["created_at"])
    assert abs((deadline - created) - timedelta(days=5)) < timedelta(minutes=1)


async def test_scan_in_prefix_is_case_insensitive(client, admin_headers, speedaf):
    response = await scan(client, admin_headers, "spd99999999")
    assert response.status_code == 200
    assert response.json()["partner_id"] == speedaf


async def test_unknown_prefix_is_rejected(client, admin_headers, speedaf):
    response = await scan(client, admin_headers, "XYZ12345678")
    assert response.status_code == 400
    assert "Unknown waybill prefix" in response.json()["detail"]


async def test_known_prefix_without_partner_record_is_rejected(client, admin_headers):
    # SPD maps to Speedaf, but Speedaf was never added as a partner
    response = await scan(client, admin_headers)
    assert response.status_code == 400
    assert "not found in system" in response.json()["detail"]


async def test_same_waybill_cannot_be_scanned_twice(client, admin_headers, speedaf):
    assert (await scan(client, admin_headers)).status_code == 200
    assert (await scan(client, admin_headers)).status_code == 400


async def test_rider_cannot_scan_in(client, admin_headers, speedaf, rider):
    _, rider_headers = rider
    assert (await scan(client, rider_headers)).status_code == 403


async def test_ops_staff_can_scan_in(client, admin_headers, speedaf):
    ops = {**RIDER, "email": "ops@example.com", "role": "ops_staff"}
    await client.post("/api/v1/users/", json=ops, headers=admin_headers)
    ops_headers = await login(client, ops["email"], ops["password"])
    assert (await scan(client, ops_headers)).status_code == 200


async def test_dispatch_assigns_rider(client, admin_headers, speedaf, rider):
    rider_id, _ = rider
    await scan(client, admin_headers)
    response = await client.patch(
        "/api/v1/parcels/dispatch", json={"waybill_number": WAYBILL, "rider_id": rider_id}, headers=admin_headers
    )
    assert response.status_code == 200, response.text
    parcel = response.json()
    assert parcel["status"] == "dispatched"
    assert parcel["rider_id"] == rider_id
    assert [e["status"] for e in parcel["history"]] == ["in_warehouse", "dispatched"]


async def test_dispatch_unknown_parcel_returns_404(client, admin_headers, rider):
    rider_id, _ = rider
    response = await client.patch(
        "/api/v1/parcels/dispatch", json={"waybill_number": "SPD00000000", "rider_id": rider_id}, headers=admin_headers
    )
    assert response.status_code == 404


async def test_status_update_is_saved_with_history(client, admin_headers, speedaf):
    await scan(client, admin_headers)
    response = await client.patch(
        "/api/v1/parcels/update-status",
        json={"waybill_number": WAYBILL, "status": "delivered", "notes": "Signed by customer"},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text

    parcel = await get_parcel(client, admin_headers)
    assert parcel["status"] == "delivered"
    assert parcel["history"][-1]["status"] == "delivered"
    assert parcel["history"][-1]["notes"] == "Signed by customer"


async def test_returned_parcel_is_unassigned_from_rider(client, admin_headers, speedaf, rider):
    rider_id, _ = rider
    await scan(client, admin_headers)
    await client.patch(
        "/api/v1/parcels/dispatch", json={"waybill_number": WAYBILL, "rider_id": rider_id}, headers=admin_headers
    )
    response = await client.patch(
        "/api/v1/parcels/update-status", json={"waybill_number": WAYBILL, "status": "returned"}, headers=admin_headers
    )
    assert response.status_code == 200, response.text

    parcel = await get_parcel(client, admin_headers)
    assert parcel["status"] == "returned"
    assert parcel["rider_id"] is None


async def test_status_update_validation(client, admin_headers, speedaf):
    await scan(client, admin_headers)
    invalid = await client.patch(
        "/api/v1/parcels/update-status", json={"waybill_number": WAYBILL, "status": "teleported"}, headers=admin_headers
    )
    assert invalid.status_code == 422
    missing = await client.patch(
        "/api/v1/parcels/update-status", json={"waybill_number": "SPD00000000", "status": "delivered"}, headers=admin_headers
    )
    assert missing.status_code == 404


async def test_overdue_list_shows_only_late_undelivered_parcels(client, admin_headers, speedaf):
    for waybill in ("SPD00000001", "SPD00000002", "SPD00000003"):
        await scan(client, admin_headers, waybill)
    await make_overdue("SPD00000001")            # late, not delivered  -> overdue
    await make_overdue("SPD00000002")            # late, but delivered  -> not overdue
    await client.patch(
        "/api/v1/parcels/update-status", json={"waybill_number": "SPD00000002", "status": "delivered"}, headers=admin_headers
    )
    # SPD00000003 is still within its deadline -> not overdue

    response = await client.get("/api/v1/parcels/overdue-delivery", headers=admin_headers)
    assert response.status_code == 200
    assert [p["waybill_number"] for p in response.json()] == ["SPD00000001"]


async def test_parcel_routes_need_login(client):
    assert (await client.get("/api/v1/parcels/")).status_code == 401
    assert (await client.post("/api/v1/parcels/scan-in", json={"waybill_number": WAYBILL})).status_code == 401
