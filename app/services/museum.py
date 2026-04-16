import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.museum import Country, City, Museum, Hall
from app.schemas.museum import CountryCreate, CityCreate, MuseumCreate, MuseumUpdate, HallCreate
from app.core.exceptions import NotFoundException, BadRequestException


# ── Country ───────────────────────────────────────────────────────

async def get_all_countries(db: AsyncSession) -> list[Country]:
    result = await db.execute(select(Country).order_by(Country.name))
    return result.scalars().all()


async def create_country(db: AsyncSession, data: CountryCreate) -> Country:
    existing = await db.execute(select(Country).where(Country.name == data.name))
    if existing.scalar_one_or_none():
        raise BadRequestException("Country already exists")
    country = Country(**data.model_dump())
    db.add(country)
    await db.commit()
    await db.refresh(country)
    return country


async def delete_country(db: AsyncSession, country_id: uuid.UUID) -> None:
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()
    if not country:
        raise NotFoundException("Country not found")
    await db.delete(country)
    await db.commit()


# ── City ──────────────────────────────────────────────────────────

async def get_cities_by_country(db: AsyncSession, country_id: uuid.UUID) -> list[City]:
    result = await db.execute(select(City).where(City.country_id == country_id).order_by(City.name))
    return result.scalars().all()


async def create_city(db: AsyncSession, data: CityCreate) -> City:
    country = await db.execute(select(Country).where(Country.id == data.country_id))
    if not country.scalar_one_or_none():
        raise NotFoundException("Country not found")
    city = City(**data.model_dump())
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city


async def delete_city(db: AsyncSession, city_id: uuid.UUID) -> None:
    result = await db.execute(select(City).where(City.id == city_id))
    city = result.scalar_one_or_none()
    if not city:
        raise NotFoundException("City not found")
    await db.delete(city)
    await db.commit()


# ── Museum ────────────────────────────────────────────────────────

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


# ── Hall ──────────────────────────────────────────────────────────

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
