from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerOut

router = APIRouter()

@router.post("/", response_model=PartnerOut)
async def create_partner(
    partner_in: PartnerCreate, 
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user) # Only logged in users can add partners
):
    """Adds a new logistics partner like Speedaf or GIG."""
    # Check if partner already exists
    result = await db.execute(select(Partner).where(Partner.name == partner_in.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Partner already exists")

    new_partner = Partner(name=partner_in.name, contact_phone=partner_in.contact_phone)
    db.add(new_partner)
    await db.commit()
    await db.refresh(new_partner)
    return new_partner

@router.get("/", response_model=List[PartnerOut])
async def list_partners(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Returns all logistics partners."""
    result = await db.execute(select(Partner))
    return result.scalars().all()