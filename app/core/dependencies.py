from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    token = credentials.credentials
    user_id = decode_token(token)
    if not user_id:
        raise UnauthorizedException("Invalid or expired token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))

    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


async def get_current_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise ForbiddenException("Admin access required")
    return user
