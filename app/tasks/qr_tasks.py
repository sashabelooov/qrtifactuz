import uuid
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.services.qr_service import generate_qr_png, save_qr_locally
from app.core.config import settings
from app.core.database import engine


def _save_sync(model_class, record_id: str, qr_url: str):
    from sqlalchemy import create_engine as _ce
    sync_url = str(engine.url).replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    sync_engine = _ce(sync_url)
    with Session(sync_engine) as session:
        session.execute(
            update(model_class)
            .where(model_class.id == uuid.UUID(record_id))
            .values(qr_code_url=qr_url)
        )
        session.commit()
    sync_engine.dispose()


@celery_app.task
def generate_museum_qr(museum_id: str, museum_slug: str):
    from app.models.museum import Museum
    url = f"{settings.FRONTEND_URL}/museum/{museum_slug}"
    png = generate_qr_png(url)
    qr_url = save_qr_locally(png, f"museum_{museum_id}.png")
    _save_sync(Museum, museum_id, qr_url)


@celery_app.task
def generate_exhibit_qr(exhibit_id: str, exhibit_slug: str):
    from app.models.exhibit import Exhibit
    url = f"{settings.FRONTEND_URL}/exhibit/{exhibit_slug}"
    png = generate_qr_png(url)
    qr_url = save_qr_locally(png, f"exhibit_{exhibit_id}.png")
    _save_sync(Exhibit, exhibit_id, qr_url)
