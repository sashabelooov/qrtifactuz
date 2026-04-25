import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.exhibit import Exhibit, ExhibitTranslation, ExhibitStatus
from app.models.museum import Museum, City
from app.schemas.exhibit import ExhibitCreate, ExhibitUpdate, ExhibitStatusUpdate
from app.core.exceptions import NotFoundException, BadRequestException


def _with_city(query):
    return (
        query
        .join(Museum, Exhibit.museum_id == Museum.id)
        .outerjoin(City, Museum.city_id == City.id)
        .add_columns(City.name.label("city_name"))
    )


def _apply_city(rows) -> list[Exhibit]:
    exhibits = []
    for row in rows:
        exhibit = row[0]
        city_name = row[1]
        exhibit.city = city_name
        exhibits.append(exhibit)
    return exhibits


async def get_all_exhibits(
    db: AsyncSession,
    museum_id: uuid.UUID | None = None,
    status: ExhibitStatus | None = None,
) -> list[Exhibit]:
    query = _with_city(select(Exhibit))

    if museum_id:
        query = query.where(Exhibit.museum_id == museum_id)
    if status:
        query = query.where(Exhibit.status == status)

    result = await db.execute(query)
    return _apply_city(result.all())


async def get_exhibit_by_slug(db: AsyncSession, slug: str) -> Exhibit:
    result = await db.execute(_with_city(select(Exhibit)).where(Exhibit.slug == slug))
    row = result.one_or_none()
    if not row:
        raise NotFoundException("Exhibit not found")
    exhibit, city_name = row
    exhibit.city = city_name
    return exhibit


async def get_exhibit_by_id(db: AsyncSession, exhibit_id: uuid.UUID) -> Exhibit:
    result = await db.execute(_with_city(select(Exhibit)).where(Exhibit.id == exhibit_id))
    row = result.one_or_none()
    if not row:
        raise NotFoundException("Exhibit not found")
    exhibit, city_name = row
    exhibit.city = city_name
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
