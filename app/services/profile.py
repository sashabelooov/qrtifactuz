import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.profile import Profile
from app.models.user import User


async def get_profile(db: AsyncSession, profile_id: uuid.UUID, current_user: User) -> Profile:
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise NotFoundException("Profile not found")

    if profile.user_id != current_user.id:
        raise ForbiddenException("You can only view your own profile")

    return profile


async def update_profile(db: AsyncSession, profile_id: uuid.UUID, data: dict, current_user: User) -> Profile:
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise NotFoundException("Profile not found")

    if profile.user_id != current_user.id:
        raise ForbiddenException("You can only update your own profile")

    if "phone" in data and data["phone"] is not None:
        current_user.phone = data.pop("phone")
        db.add(current_user)

    for key, value in data.items():
        if value is not None:
            setattr(profile, key, value)

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return profile
