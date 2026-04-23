import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    cities: Mapped[list["City"]] = relationship("City", back_populates="country", lazy="selectin")

    def __repr__(self) -> str:
        return self.name


class City(Base):
    __tablename__ = "cities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    country: Mapped["Country"] = relationship("Country", back_populates="cities", lazy="noload")
    museums: Mapped[list["Museum"]] = relationship("Museum", back_populates="city_rel", lazy="noload")

    def __repr__(self) -> str:
        return self.name


class Museum(Base):
    __tablename__ = "museums"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    qr_code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(server_default=func.now())
    updated_at: Mapped[str] = mapped_column(server_default=func.now(), onupdate=func.now())

    city_rel: Mapped["City | None"] = relationship("City", back_populates="museums", lazy="selectin")
    exhibits: Mapped[list["Exhibit"]] = relationship("Exhibit", back_populates="museum", lazy="noload", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self) -> str:
        return self.name
