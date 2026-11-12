"""Dashboard numbers must match what is actually in the database."""
from tests.integration.conftest import make_overdue
from tests.integration.test_parcels import scan


async def set_status(client, headers, waybill, status):
    r = await client.patch(
        "/api/v1/parcels/update-status", json={"waybill_number": waybill, "status": status}, headers=headers
    )
    assert r.status_code == 200, r.text


async def test_empty_dashboard(client, admin_headers):
    stats = (await client.get("/api/v1/dashboard/stats", headers=admin_headers)).json()
    assert stats == {
        "total_by_status": {"in_warehouse": 0, "dispatched": 0, "delivered": 0, "delivery_failed": 0, "returned": 0},
        "delivery_sla_breaches": 0,
        "rider_workload": {},
        "efficiency_score": 100.0,
    }


async def test_dashboard_counts_efficiency_breaches_and_workload(client, admin_headers, speedaf, rider):
    rider_id, _ = rider
    waybills = ["SPD00000001", "SPD00000002", "SPD00000003", "SPD00000004"]
    for w in waybills:
        await scan(client, admin_headers, w)

    # SPD...1: the rider delivered it. It must NOT count towards their current workload.
    await client.patch(
        "/api/v1/parcels/dispatch", json={"waybill_number": "SPD00000001", "rider_id": rider_id}, headers=admin_headers
    )
    await set_status(client, admin_headers, "SPD00000001", "delivered")
    await set_status(client, admin_headers, "SPD00000002", "returned")
    # SPD...3: currently out with the rider
    await client.patch(
        "/api/v1/parcels/dispatch", json={"waybill_number": "SPD00000003", "rider_id": rider_id}, headers=admin_headers
    )
    # Two real breaches: SPD...3 is late while out with the rider, and SPD...4 is
    # late in the warehouse. (Every parcel is now overdue, so a reversed date
    # comparison would report 0 instead of 2.)
    await make_overdue("SPD00000003")
    await make_overdue("SPD00000004")
    # Late but finished (delivered / returned) parcels are NOT breaches
    await make_overdue("SPD00000001")
    await make_overdue("SPD00000002")

    stats = (await client.get("/api/v1/dashboard/stats", headers=admin_headers)).json()
    assert stats["total_by_status"] == {
        "in_warehouse": 1, "dispatched": 1, "delivered": 1, "delivery_failed": 0, "returned": 1,
    }
    # (delivered 1 + returned 1) / 4 parcels = 50%
    assert stats["efficiency_score"] == 50.0
    assert stats["delivery_sla_breaches"] == 2
    assert stats["rider_workload"] == {"Rex Rider": 1}


async def test_dashboard_needs_login(client):
    assert (await client.get("/api/v1/dashboard/stats")).status_code == 401
