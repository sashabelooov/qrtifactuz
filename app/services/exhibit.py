import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.exhibit import Exhibit, ExhibitTranslation, ExhibitStatus
from app.schemas.exhibit import ExhibitCreate, ExhibitUpdate, ExhibitStatusUpdate
from app.core.exceptions import NotFoundException, BadRequestException


async def get_all_exhibits(
    db: AsyncSession,
    museum_id: uuid.UUID | None = None,
    status: ExhibitStatus | None = None,
    hall_id: uuid.UUID | None = None,
) -> list[Exhibit]:
    query = select(Exhibit)

    if museum_id:
        query = query.where(Exhibit.museum_id == museum_id)
    if status:
        query = query.where(Exhibit.status == status)
    if hall_id:
        query = query.where(Exhibit.hall_id == hall_id)

    result = await db.execute(query)
    return result.scalars().all()


async def get_exhibit_by_slug(db: AsyncSession, slug: str) -> Exhibit:
    result = await db.execute(select(Exhibit).where(Exhibit.slug == slug))
    exhibit = result.scalar_one_or_none()
    if not exhibit:
        raise NotFoundException("Exhibit not found")
    return exhibit


async def get_exhibit_by_id(db: AsyncSession, exhibit_id: uuid.UUID) -> Exhibit:
    result = await db.execute(select(Exhibit).where(Exhibit.id == exhibit_id))
    exhibit = result.scalar_one_or_none()
    if not exhibit:
        raise NotFoundException("Exhibit not found")
    return exhibit


async def create_exhibit(
    db: AsyncSession,
    data: ExhibitCreate,
    created_by: uuid.UUID,
) -> Exhibit:
    existing = await db.execute(select(Exhibit).where(Exhibit.slug == data.slug))
    if existing.scalar_one_or_none():
        raise BadRequestException("Exhibit with this slug already exists")

    exhibit = Exhibit(
        museum_id=data.museum_id,
        hall_id=data.hall_id,
        slug=data.slug,
        created_by=created_by,
    )
    db.add(exhibit)
    await db.flush()

    for t in data.translations:
        translation = ExhibitTranslation(exhibit_id=exhibit.id, **t.model_dump())
        db.add(translation)

    await db.commit()
    await db.refresh(exhibit)
    return exhibit


async def update_exhibit(
    db: AsyncSession,
    exhibit_id: uuid.UUID,
    data: ExhibitUpdate,
) -> Exhibit:
    exhibit = await get_exhibit_by_id(db, exhibit_id)
    update_data = data.model_dump(exclude_unset=True)

    translations = update_data.pop("translations", None)

    for key, value in update_data.items():
        setattr(exhibit, key, value)

    if translations is not None:
        await db.execute(
            __import__("sqlalchemy").delete(ExhibitTranslation).where(
                ExhibitTranslation.exhibit_id == exhibit_id
            )
        )
        for t in translations:
            translation = ExhibitTranslation(exhibit_id=exhibit.id, **t)
            db.add(translation)

    await db.commit()
    await db.refresh(exhibit)
    return exhibit


async def update_exhibit_status(
    db: AsyncSession,
    exhibit_id: uuid.UUID,
    data: ExhibitStatusUpdate,
) -> Exhibit:
    exhibit = await get_exhibit_by_id(db, exhibit_id)
    exhibit.status = data.status
    await db.commit()
    await db.refresh(exhibit)
    return exhibit


async def delete_exhibit(db: AsyncSession, exhibit_id: uuid.UUID) -> None:
    exhibit = await get_exhibit_by_id(db, exhibit_id)
    await db.delete(exhibit)
    await db.commit()


async def increment_views(db: AsyncSession, exhibit_id: uuid.UUID) -> None:
    await db.execute(
        update(Exhibit)
        .where(Exhibit.id == exhibit_id)
        .values(views_count=Exhibit.views_count + 1)
    )
    await db.commit()


async def increment_listens(db: AsyncSession, exhibit_id: uuid.UUID) -> None:
    await db.execute(
        update(Exhibit)
        .where(Exhibit.id == exhibit_id)
        .values(listens_count=Exhibit.listens_count + 1)
    )
    await db.commit()
