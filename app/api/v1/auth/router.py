from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse, VerifyEmailRequest
from app.services.auth import login_user, refresh_tokens, register_user, verify_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(db, body.email, body.password)


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email_route(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await verify_email(db, body.email, body.otp)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(db, body.email, body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(db, body.refresh_token)


@router.post("/logout", status_code=204)
async def logout(current_user=Depends(get_current_user)):
    return None


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user
