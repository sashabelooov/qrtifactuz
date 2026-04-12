import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.museum import Museum, Hall
from app.schemas.museum import MuseumCreate, MuseumUpdate, HallCreate
from app.core.exceptions import NotFoundException, BadRequestException


async def get_all_museums(db: AsyncSession) -> list[Museum]:
    result = await db.execute(select(Museum).where(Museum.is_active == True))
    return result.scalars().all()


async def get_museum_by_id(db: AsyncSession, museum_id: uuid.UUID) -> Museum:
    result = await db.execute(select(Museum).where(Museum.id == museum_id))
    museum = result.scalar_one_or_none()
    if not museum:
        raise NotFoundException("Museum not found")
    return museum


async def create_museum(db: AsyncSession, data: MuseumCreate) -> Museum:
    existing = await db.execute(select(Museum).where(Museum.slug == data.slug))
    if existing.scalar_one_or_none():
        raise BadRequestException("Museum with this slug already exists")

    museum = Museum(**data.model_dump())
    db.add(museum)
    await db.commit()
    await db.refresh(museum)
    return museum


async def update_museum(db: AsyncSession, museum_id: uuid.UUID, data: MuseumUpdate) -> Museum:
    museum = await get_museum_by_id(db, museum_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(museum, key, value)

    await db.commit()
    await db.refresh(museum)
    return museum


async def delete_museum(db: AsyncSession, museum_id: uuid.UUID) -> None:
    museum = await get_museum_by_id(db, museum_id)
    await db.delete(museum)
    await db.commit()


async def create_hall(db: AsyncSession, museum_id: uuid.UUID, data: HallCreate) -> Hall:
    await get_museum_by_id(db, museum_id)

    hall = Hall(museum_id=museum_id, **data.model_dump())
    db.add(hall)
    await db.commit()
    await db.refresh(hall)
    return hall


async def delete_hall(db: AsyncSession, hall_id: uuid.UUID) -> None:
    result = await db.execute(select(Hall).where(Hall.id == hall_id))
    hall = result.scalar_one_or_none()
    if not hall:
        raise NotFoundException("Hall not found")
    await db.delete(hall)
    await db.commit()
