import uuid
import enum
from sqlalchemy import String, Text, Boolean, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ExhibitStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class LanguageCode(str, enum.Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"


class Exhibit(Base):
    __tablename__ = "exhibits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    museum_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("museums.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    qr_code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ExhibitStatus] = mapped_column(Enum(ExhibitStatus), default=ExhibitStatus.draft)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    listens_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(server_default=func.now())
    updated_at: Mapped[str] = mapped_column(server_default=func.now(), onupdate=func.now())

    museum: Mapped["Museum"] = relationship("Museum", back_populates="exhibits", lazy="noload")
    translations: Mapped[list["ExhibitTranslation"]] = relationship("ExhibitTranslation", back_populates="exhibit", lazy="selectin", cascade="all, delete-orphan")
    media: Mapped[list["ExhibitMedia"]] = relationship("ExhibitMedia", back_populates="exhibit", lazy="selectin", cascade="all, delete-orphan")
    audio_tracks: Mapped[list["ExhibitAudioTrack"]] = relationship("ExhibitAudioTrack", back_populates="exhibit", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return self.slug


class ExhibitTranslation(Base):
    __tablename__ = "exhibit_translations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exhibit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exhibits.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[LanguageCode] = mapped_column(Enum(LanguageCode), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    exhibit: Mapped["Exhibit"] = relationship("Exhibit", back_populates="translations", lazy="selectin")

    def __repr__(self) -> str:
        return f"[{self.language}] {self.title}"


class ExhibitMedia(Base):
    __tablename__ = "exhibit_media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exhibit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exhibits.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), default=MediaType.image)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    exhibit: Mapped["Exhibit"] = relationship("Exhibit", back_populates="media", lazy="selectin")

    def __repr__(self) -> str:
        return f"{self.media_type}: {self.public_url}"


class ExhibitAudioTrack(Base):
    __tablename__ = "exhibit_audio_tracks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exhibit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exhibits.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[LanguageCode] = mapped_column(Enum(LanguageCode), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    exhibit: Mapped["Exhibit"] = relationship("Exhibit", back_populates="audio_tracks", lazy="selectin")

    def __repr__(self) -> str:
        return f"[{self.language}] {self.public_url}"
