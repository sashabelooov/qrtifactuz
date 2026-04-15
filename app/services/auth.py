import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.models.profile import Profile
from app.services.otp import generate_otp, save_otp, verify_otp, delete_otp
from app.services.email import send_otp_email


async def register_user(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise BadRequestException("Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=False,
    )
    db.add(user)
    await db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    otp = generate_otp()
    await save_otp(str(user.id), otp)
    await send_otp_email(email, otp)

    return {"message": "Registration successful. Check your email for the verification code."}


async def verify_email(db: AsyncSession, email: str, otp: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise BadRequestException("User not found")

    if user.is_active:
        raise BadRequestException("Account already verified")

    is_valid = await verify_otp(str(user.id), otp)
    if not is_valid:
        raise BadRequestException("Invalid or expired verification code")

    user.is_active = True
    await db.commit()
    await delete_otp(str(user.id))

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }


async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException("Account not verified. Check your email for the verification code.")

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    user_id = decode_token(refresh_token)
    if not user_id:
        raise UnauthorizedException("Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }
