from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from app.models.user import User, UserRole
from app.services import user_svc
from app.schemas.user import UserCreate, UserOut
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    One-time bootstrap: creates the FIRST user of the system, always as an admin.
    Once any user exists this endpoint is permanently closed; admins then
    create staff and riders through the protected POST /users/ route.
    """
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signup is closed. Ask an admin to create your account."
        )

    # Whatever role was requested, the bootstrap user is the admin
    user_in = user_in.model_copy(update={"role": UserRole.ADMIN})
    return await user_svc.create_user(db, user_in)

@router.post("/login")
async def login(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Logs in a user and returns a JWT token."""
    # 1. Find user by email (FastAPI uses 'username' field for email in forms)
    user = await user_svc.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 2. Generate Token
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}