from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserCreate
from app.services import user_svc
from app.api.dependencies import check_admin

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/team/{role}", response_model=List[UserOut])
async def get_users_by_role(
    role: UserRole, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Example: GET /users/team/rider returns all riders.
    """
    # Only Admin and Ops Staff should be able to see the rider list
    if current_user.role not in [UserRole.ADMIN, UserRole.OPS_STAFF]:
        raise HTTPException(status_code=403, detail="Not authorized to view team lists")
        
    result = await db.execute(select(User).where(User.role == role))
    return result.scalars().all()

@router.get("/operations/riders", response_model=List[UserOut])
async def get_delivery_personnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns everyone who delivers (Riders + Foot Couriers)."""
    result = await db.execute(
        select(User).where(User.role.in_([UserRole.RIDER, UserRole.FOOT_COURIER]))
    )
    return result.scalars().all()

@router.post("/", response_model=UserOut)
async def create_new_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(check_admin) # PROTECTION HERE
):
    """
    Admin creates a new staff member or rider.
    """
    existing_user = await user_svc.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return await user_svc.create_user(db, user_in)

@router.get("/", response_model=List[UserOut])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(check_admin) # PROTECTION HERE
):
    """
    Returns a list of every staff member and rider in the system.
    """
    result = await db.execute(select(User))
    return result.scalars().all()

@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(check_admin)
):
    """
    Allows Admin to remove a staff member or rider.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}