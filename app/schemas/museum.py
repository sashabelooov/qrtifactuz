import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional


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
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Uzbekistan"
    logo_url: Optional[str] = None


class MuseumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class MuseumResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    logo_url: Optional[str] = None
    is_active: bool
    halls: list[HallResponse] = []
