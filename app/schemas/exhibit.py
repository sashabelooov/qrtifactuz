import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.exhibit import ExhibitStatus, LanguageCode, MediaType


class ExhibitTranslationCreate(BaseModel):
    language: LanguageCode
    title: str
    description: Optional[str] = None


class ExhibitTranslationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    language: LanguageCode
    title: str
    description: Optional[str] = None
    audio_url: Optional[str] = None
    media_url: Optional[str] = None


class ExhibitMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    public_url: str
    media_type: MediaType
    is_cover: bool
    sort_order: int


class ExhibitAudioTrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    language: LanguageCode
    public_url: str
    duration_seconds: Optional[float] = None


class ExhibitCreate(BaseModel):
    museum_id: uuid.UUID
    slug: str
    city: Optional[str] = None
    translations: list[ExhibitTranslationCreate] = []


class ExhibitUpdate(BaseModel):
    slug: Optional[str] = None
    city: Optional[str] = None
    status: Optional[ExhibitStatus] = None
    translations: Optional[list[ExhibitTranslationCreate]] = None


class ExhibitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    museum_id: uuid.UUID
    slug: str
    city: Optional[str] = None
    qr_code_url: Optional[str] = None
    status: ExhibitStatus
    views_count: int
    listens_count: int
    translations: list[ExhibitTranslationResponse] = []


class ExhibitStatusUpdate(BaseModel):
    status: ExhibitStatus
