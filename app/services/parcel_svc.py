import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.models.parcel import Parcel, TrackingEvent, ParcelStatus
from app.models.partner import Partner # Added this to lookup partners

# 1. THE BRAIN: Prefix to Partner Mapping
# Make sure these names match exactly what you have in your Partners table!
PREFIX_MAP = {
    "SPD": "Speedaf",
    "GIG": "GIG Logistics",
    "SHP": "Sharp Courier",
    "DNG": "Dang",
}

async def mock_external_fetch(waybill: str):
    """
    Simulates fetching data from Speedaf/GIG servers.
    In the real world, this would be an API call.
    """
    await asyncio.sleep(0.5) # Simulate a fast network response
    
    # We generate semi-realistic data based on the waybill number
    return {
        "name": f"Recipient for {waybill}",
        "phone": "080" + waybill[-8:] if len(waybill) > 8 else "08012345678",
        "address": "Auto-Fetched: Plot " + waybill[-2:] + ", Commercial Way, Lagos State"
    }

async def scan_in_parcel(db: AsyncSession, waybill_number: str, user_id: int):
    """
    The New "Magic" Scan:
    1. Identifies Partner from Prefix
    2. Fetches details automatically
    3. Saves to Database
    """
    # Step A: Identify the Partner via Prefix (e.g. SPD-123)
    detected_partner_name = None
    waybill_upper = waybill_number.upper()
    
    for prefix, name in PREFIX_MAP.items():
        if waybill_upper.startswith(prefix):
            detected_partner_name = name
            break
    
    if not detected_partner_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown waybill prefix. Please use {', '.join(PREFIX_MAP.keys())}"
        )

    # Step B: Get the Partner ID from the database
    partner_query = await db.execute(
        select(Partner).where(Partner.name == detected_partner_name)
    )
    partner = partner_query.scalars().first()
    
    if not partner:
        raise HTTPException(
            status_code=400, 
            detail=f"Partner '{detected_partner_name}' recognized but not found in system. Please add them first."
        )

    # Step C: Mock the data fetch (No more manual typing!)
    external_data = await mock_external_fetch(waybill_number)

    # Step D: Create the Parcel
    new_parcel = Parcel(
        waybill_number=waybill_number,
        partner_id=partner.id,
        recipient_name=external_data["name"],
        recipient_phone=external_data["phone"],
        delivery_address=external_data["address"],
        status=ParcelStatus.IN_WAREHOUSE
    )
    db.add(new_parcel)
    await db.flush() 

    # Step E: Create the Tracking Event (Audit Trail)
    event = TrackingEvent(
        parcel_id=new_parcel.id,
        status=ParcelStatus.IN_WAREHOUSE,
        notes=f"Auto-scan success. Partner detected: {partner.name}",
        updated_by_id=user_id
    )
    db.add(event)
    
    await db.commit()
    
    # Re-query to return full object with history for the frontend
    result = await db.execute(
        select(Parcel)
        .where(Parcel.id == new_parcel.id)
        .options(selectinload(Parcel.history))
    )
    return result.scalars().first()

async def get_parcel_by_waybill(db: AsyncSession, waybill: str):
    """Fetch a parcel and all its history in one go."""
    result = await db.execute(
        select(Parcel)
        .where(Parcel.waybill_number == waybill)
        .options(selectinload(Parcel.history))
        # Reload from the database even if this parcel is already in the session,
        # otherwise a re-fetch after an update returns the old history
        .execution_options(populate_existing=True)
    )
    return result.scalars().first()