import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.exhibit import ExhibitStatus
from app.schemas.exhibit import ExhibitCreate, ExhibitUpdate, ExhibitResponse, ExhibitStatusUpdate
from app.services import exhibit as exhibit_service
from app.tasks.qr_tasks import generate_exhibit_qr


router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────

@router.get(
    "/exhibits",
    response_model=list[ExhibitResponse],
    tags=["Exhibits"],
    summary="List exhibits",
    description="Returns a list of exhibits. Filter by `museum_id`, `hall_id`, or `status` (draft, published, archived). Public endpoint — no authentication required.",
)
async def list_exhibits(
    museum_id: uuid.UUID | None = None,
    hall_id: uuid.UUID | None = None,
    status: ExhibitStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await exhibit_service.get_all_exhibits(db, museum_id, status, hall_id)


@router.get(
    "/exhibits/{slug}",
    response_model=ExhibitResponse,
    tags=["Exhibits"],
    summary="Get exhibit by slug",
    description="Returns full exhibit details including translations (uz/ru/en), media files, and audio tracks. The `slug` is the unique URL-friendly identifier of the exhibit.",
)
async def get_exhibit(slug: str, db: AsyncSession = Depends(get_db)):
    return await exhibit_service.get_exhibit_by_slug(db, slug)


@router.post(
    "/exhibits/{exhibit_id}/view",
    status_code=204,
    tags=["Exhibits"],
    summary="Track exhibit view",
    description="Increments the view counter for an exhibit. Call this when a visitor opens an exhibit page. No authentication required.",
)
async def view_exhibit(exhibit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await exhibit_service.increment_views(db, exhibit_id)


@router.post(
    "/exhibits/{exhibit_id}/listen",
    status_code=204,
    tags=["Exhibits"],
    summary="Track audio listen",
    description="Increments the listen counter for an exhibit. Call this when a visitor plays the audio guide. No authentication required.",
)
async def listen_exhibit(exhibit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await exhibit_service.increment_listens(db, exhibit_id)


# ── Admin endpoints ───────────────────────────────────────────────

@router.post(
    "/admin/exhibits",
    response_model=ExhibitResponse,
    status_code=201,
    tags=["Admin — Exhibits"],
    summary="Create exhibit",
    description="Creates a new exhibit with translations and media. Admin only. The exhibit is created in `draft` status — use PATCH `/status` to publish it.",
)
async def create_exhibit(
    data: ExhibitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return await exhibit_service.create_exhibit(db, data, current_user.id)


@router.put(
    "/admin/exhibits/{exhibit_id}",
    response_model=ExhibitResponse,
    tags=["Admin — Exhibits"],
    summary="Update exhibit",
    description="Updates exhibit fields and translations. Admin only. Pass only the fields you want to change.",
)
async def update_exhibit(
    exhibit_id: uuid.UUID,
    data: ExhibitUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return await exhibit_service.update_exhibit(db, exhibit_id, data)


@router.patch(
    "/admin/exhibits/{exhibit_id}/status",
    response_model=ExhibitResponse,
    tags=["Admin — Exhibits"],
    summary="Update exhibit status",
    description="Changes the exhibit status. Allowed values: `draft`, `published`, `archived`. Only `published` exhibits are visible to visitors.",
)
async def update_exhibit_status(
    exhibit_id: uuid.UUID,
    data: ExhibitStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    exhibit = await exhibit_service.update_exhibit_status(db, exhibit_id, data)
    if data.status == ExhibitStatus.published:
        generate_exhibit_qr.delay(str(exhibit.id), exhibit.slug)
    return exhibit


@router.delete(
    "/admin/exhibits/{exhibit_id}",
    status_code=204,
    tags=["Admin — Exhibits"],
    summary="Delete exhibit",
    description="Permanently deletes an exhibit and all its translations, media, and audio tracks. Admin only. This action cannot be undone.",
)
async def delete_exhibit(
    exhibit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    await exhibit_service.delete_exhibit(db, exhibit_id)
