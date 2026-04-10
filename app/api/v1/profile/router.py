import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile import get_profile, update_profile

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile_route(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_profile(db, profile_id, current_user)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile_route(
    profile_id: uuid.UUID,
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_profile(db, profile_id, body.model_dump(exclude_unset=True), current_user)
