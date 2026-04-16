import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.museum import (
    CountryCreate, CountryResponse,
    CityCreate, CityResponse,
    MuseumCreate, MuseumUpdate, MuseumResponse,
    HallCreate, HallResponse,
)
from app.services import museum as museum_service

router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────

@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(db: AsyncSession = Depends(get_db)):
    return await museum_service.get_all_countries(db)


@router.get("/countries/{country_id}/cities", response_model=list[CityResponse])
async def list_cities(country_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await museum_service.get_cities_by_country(db, country_id)


@router.get("/museums", response_model=list[MuseumResponse])
async def list_museums(db: AsyncSession = Depends(get_db)):
    return await museum_service.get_all_museums(db)


@router.get("/museums/{museum_id}", response_model=MuseumResponse)
async def get_museum(museum_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await museum_service.get_museum_by_id(db, museum_id)


# ── Admin endpoints ───────────────────────────────────────────────

@router.post("/admin/countries", response_model=CountryResponse, status_code=201)
async def create_country(
    data: CountryCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_country(db, data)


@router.delete("/admin/countries/{country_id}", status_code=204)
async def delete_country(
    country_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_country(db, country_id)


@router.post("/admin/cities", response_model=CityResponse, status_code=201)
async def create_city(
    data: CityCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_city(db, data)


@router.delete("/admin/cities/{city_id}", status_code=204)
async def delete_city(
    city_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_city(db, city_id)


@router.post("/admin/museums", response_model=MuseumResponse, status_code=201)
async def create_museum(
    data: MuseumCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_museum(db, data)


@router.put("/admin/museums/{museum_id}", response_model=MuseumResponse)
async def update_museum(
    museum_id: uuid.UUID,
    data: MuseumUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.update_museum(db, museum_id, data)


@router.delete("/admin/museums/{museum_id}", status_code=204)
async def delete_museum(
    museum_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_museum(db, museum_id)


@router.post("/admin/museums/{museum_id}/halls", response_model=HallResponse, status_code=201)
async def create_hall(
    museum_id: uuid.UUID,
    data: HallCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_hall(db, museum_id, data)


@router.delete("/admin/halls/{hall_id}", status_code=204)
async def delete_hall(
    hall_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_hall(db, hall_id)
