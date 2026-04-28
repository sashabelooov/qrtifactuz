import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.museum import (
    CountryCreate, CountryResponse,
    CityCreate, CityResponse,
    MuseumCreate, MuseumUpdate, MuseumResponse, MuseumDetailResponse,
)
from app.services import museum as museum_service
router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────

@router.get(
    "/countries",
    response_model=list[CountryResponse],
    tags=["Geography"],
    summary="List all countries",
    description="Returns all countries that have museums registered. Use this to build country filter dropdowns.",
)
async def list_countries(db: AsyncSession = Depends(get_db)):
    return await museum_service.get_all_countries(db)


@router.get(
    "/countries/{country_id}/cities",
    response_model=list[CityResponse],
    tags=["Geography"],
    summary="List cities by country",
    description="Returns all cities within a given country that have museums. Use `country_id` from the `/countries` endpoint.",
)
async def list_cities(country_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await museum_service.get_cities_by_country(db, country_id)


@router.get(
    "/museums",
    response_model=list[MuseumResponse],
    tags=["Museums"],
    summary="List all museums",
    description="Returns all active museums including their halls. No authentication required.",
)
async def list_museums(db: AsyncSession = Depends(get_db)):
    return await museum_service.get_all_museums(db)


@router.get(
    "/museums/{museum_id}",
    response_model=MuseumResponse,
    tags=["Museums"],
    summary="Get museum by ID",
    description="Returns a single museum with full details.",
)
async def get_museum(museum_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await museum_service.get_museum_by_id(db, museum_id)


@router.get(
    "/museums/{museum_id}/exhibits",
    response_model=MuseumDetailResponse,
    tags=["Museums"],
    summary="Get museum with all its exhibits",
    description="Returns museum info plus all published exhibits with translations, audio, and media.",
)
async def get_museum_with_exhibits(museum_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await museum_service.get_museum_with_exhibits(db, museum_id)


# ── Admin endpoints ───────────────────────────────────────────────

@router.post(
    "/admin/countries",
    response_model=CountryResponse,
    status_code=201,
    tags=["Admin — Geography"],
    summary="Create country",
    description="Creates a new country. Admin only.",
)
async def create_country(
    data: CountryCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_country(db, data)


@router.delete(
    "/admin/countries/{country_id}",
    status_code=204,
    tags=["Admin — Geography"],
    summary="Delete country",
    description="Deletes a country. Admin only. Will fail if cities or museums are linked to it.",
)
async def delete_country(
    country_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_country(db, country_id)


@router.post(
    "/admin/cities",
    response_model=CityResponse,
    status_code=201,
    tags=["Admin — Geography"],
    summary="Create city",
    description="Creates a new city linked to a country. Admin only.",
)
async def create_city(
    data: CityCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_city(db, data)


@router.delete(
    "/admin/cities/{city_id}",
    status_code=204,
    tags=["Admin — Geography"],
    summary="Delete city",
    description="Deletes a city. Admin only. Will fail if museums are linked to it.",
)
async def delete_city(
    city_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_city(db, city_id)


@router.post(
    "/admin/museums",
    response_model=MuseumResponse,
    status_code=201,
    tags=["Admin — Museums"],
    summary="Create museum",
    description="Creates a new museum. Admin only. The museum will be visible to visitors once it has published exhibits.",
)
async def create_museum(
    data: MuseumCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.create_museum(db, data)




@router.put(
    "/admin/museums/{museum_id}",
    response_model=MuseumResponse,
    tags=["Admin — Museums"],
    summary="Update museum",
    description="Updates museum details such as name, description, address, or logo. Admin only.",
)
async def update_museum(
    museum_id: uuid.UUID,
    data: MuseumUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    return await museum_service.update_museum(db, museum_id, data)


@router.delete(
    "/admin/museums/{museum_id}",
    status_code=204,
    tags=["Admin — Museums"],
    summary="Delete museum",
    description="Permanently deletes a museum and all its halls. Admin only. This action cannot be undone.",
)
async def delete_museum(
    museum_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    await museum_service.delete_museum(db, museum_id)


