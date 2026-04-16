import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional


class CountryCreate(BaseModel):
    name: str
    code: Optional[str] = None


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: Optional[str] = None


class CityCreate(BaseModel):
    name: str
    country_id: uuid.UUID


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    country_id: uuid.UUID


class HallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    museum_id: uuid.UUID
    name: str
    description: Optional[str] = None
    floor: Optional[int] = None


class HallCreate(BaseModel):
    name: str
    description: Optional[str] = None
    floor: Optional[int] = None


class MuseumCreate(BaseModel):
    name: str
    slug: str
    city_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None


class MuseumUpdate(BaseModel):
    name: Optional[str] = None
    city_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class MuseumResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    city_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    halls: list[HallResponse] = []
