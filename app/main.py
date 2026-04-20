import uuid
import asyncio
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import FileField
from app.api.v1.museum.router import router as museums_router
from app.models.user import User
from app.models.museum import Country, City, Museum, Hall
from fastapi.staticfiles import StaticFiles



from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.api.v1.auth.router import router as auth_router
from app.api.v1.profile.router import router as profiles_router
from app.core.database import engine
from app.api.v1.exhibits.router import router as exhibits_router
from app.models.exhibit import Exhibit, ExhibitTranslation, ExhibitMedia, ExhibitAudioTrack



app = FastAPI(
    title="QRTifact API",
    version="1.0.0",
    description=(
        "Backend API for QRTifact — a multilingual museum exhibit platform for Uzbekistan.\n\n"
        "Visitors scan QR codes to explore exhibits in **Uzbek**, **Russian**, or **English**.\n\n"
        "## Authentication\n"
        "Most endpoints require a Bearer token. Get one via `POST /api/v1/auth/login` or Google OAuth.\n"
        "Pass it as: `Authorization: Bearer <access_token>`\n\n"
        "## Admin endpoints\n"
        "Endpoints under `/admin/` require an admin account (`is_admin = true`).\n\n"
        "## Languages\n"
        "Supported language codes: `uz` (Uzbek), `ru` (Russian), `en` (English)."
    ),
    debug=settings.DEBUG,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=settings.ADMIN_SECRET_KEY)


class AdminI18nMiddleware(BaseHTTPMiddleware):
    """Injects admin_i18n.js into every admin HTML page."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if (
            request.url.path.startswith("/admin")
            and "text/html" in response.headers.get("content-type", "")
        ):
            body = b"".join([chunk async for chunk in response.body_iterator])
            body = body.replace(
                b"</body>",
                b'<script src="/static/admin_i18n.js"></script></body>',
            )
            headers = dict(response.headers)
            headers["content-length"] = str(len(body))
            return Response(content=body, status_code=response.status_code,
                            headers=headers, media_type=response.media_type)
        return response


app.add_middleware(AdminI18nMiddleware)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form.get("username") == settings.ADMIN_USERNAME and form.get("password") == settings.ADMIN_PASSWORD:
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin", False)


admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.ADMIN_SECRET_KEY))


def _upload_file(content: bytes, filename: str, folder: str) -> tuple[str, str]:
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        key = f"{folder}/{uuid.uuid4()}/{filename}"
        s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=content)
        public_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"
        return key, public_url
    else:
        import os
        local_dir = f"static/uploads/{folder}"
        os.makedirs(local_dir, exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{filename}"
        local_path = f"{local_dir}/{unique_name}"
        with open(local_path, "wb") as f:
            f.write(content)
        public_url = f"{settings.BACKEND_URL}/static/uploads/{folder}/{unique_name}"
        return local_path, public_url


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    column_list = [User.email, User.is_active, User.is_admin, User.created_at, User.id]
    column_searchable_list = [User.email]
    column_labels = {"is_active": "Active", "is_admin": "Admin", "created_at": "Created"}
    can_delete = True


class CountryAdmin(ModelView, model=Country):
    name = "Country"
    name_plural = "Countries"
    icon = "fa-solid fa-earth-asia"
    column_list = [Country.name, Country.code, Country.created_at, Country.id]
    column_searchable_list = [Country.name]
    column_labels = {"created_at": "Created"}
    form_excluded_columns = ["created_at", "cities"]
    can_delete = True


class CityAdmin(ModelView, model=City):
    name = "City"
    name_plural = "Cities"
    icon = "fa-solid fa-city"
    column_list = [City.name, City.country_id, City.created_at, City.id]
    column_searchable_list = [City.name]
    column_labels = {"country_id": "Country", "created_at": "Created"}
    form_excluded_columns = ["created_at", "museums"]
    can_delete = True


class MuseumAdmin(ModelView, model=Museum):
    name = "Museum"
    name_plural = "Museums"
    icon = "fa-solid fa-landmark"
    column_list = [Museum.name, Museum.slug, Museum.city_id, Museum.is_active, Museum.qr_code_url, Museum.id]
    column_searchable_list = [Museum.name, Museum.slug]
    column_labels = {"city_id": "City", "is_active": "Active", "qr_code_url": "QR Code URL"}
    form_excluded_columns = ["created_at", "updated_at", "halls"]
    can_delete = True

    async def after_model_change(self, data, model, is_created, request):
        if is_created:
            from app.tasks.qr_tasks import generate_museum_qr
            generate_museum_qr.delay(str(model.id), model.slug)


class HallAdmin(ModelView, model=Hall):
    name = "Hall"
    name_plural = "Halls"
    icon = "fa-solid fa-door-open"
    column_list = [Hall.name, Hall.museum_id, Hall.floor, Hall.id]
    column_labels = {"museum_id": "Museum"}
    form_excluded_columns = ["created_at", "updated_at"]
    can_delete = True


class ExhibitAdmin(ModelView, model=Exhibit):
    name = "Exhibit"
    name_plural = "Exhibits"
    icon = "fa-solid fa-image"
    column_list = [Exhibit.slug, Exhibit.status, Exhibit.views_count, Exhibit.listens_count, Exhibit.id]
    column_searchable_list = [Exhibit.slug]
    column_labels = {
        "museum": "Museum", "hall": "Hall", "created_by": "Created By",
        "qr_code_url": "QR Code URL", "views_count": "Views", "listens_count": "Listens",
        "created_at": "Created", "updated_at": "Updated",
    }
    form_columns = ["museum", "hall", "slug", "qr_code_url", "status"]
    can_delete = True


class ExhibitTranslationAdmin(ModelView, model=ExhibitTranslation):
    name = "Translation"
    name_plural = "Translations"
    icon = "fa-solid fa-language"
    column_list = [ExhibitTranslation.exhibit, ExhibitTranslation.language, ExhibitTranslation.title, ExhibitTranslation.id]
    column_labels = {"exhibit": "Exhibit", "language": "Language", "title": "Title", "description": "Description"}
    form_columns = ["exhibit", "language", "title", "description"]
    can_delete = True


class ExhibitAudioTrackAdmin(ModelView, model=ExhibitAudioTrack):
    name = "Audio Track"
    name_plural = "Audio Tracks"
    icon = "fa-solid fa-headphones"
    column_list = [ExhibitAudioTrack.exhibit, ExhibitAudioTrack.language, ExhibitAudioTrack.public_url, ExhibitAudioTrack.duration_seconds, ExhibitAudioTrack.id]
    column_labels = {
        "exhibit": "Exhibit", "language": "Language",
        "storage_path": "File", "public_url": "Public URL", "duration_seconds": "Duration (sec)",
    }
    form_overrides = {"storage_path": FileField}
    form_columns = ["exhibit", "language", "storage_path", "duration_seconds"]
    can_delete = True

    async def on_model_change(self, data, model, is_created, request):
        file = data.get("storage_path")
        if file and hasattr(file, "filename") and file.filename:
            content = await file.read()
            key, url = await asyncio.get_event_loop().run_in_executor(
                None, _upload_file, content, file.filename, "audio"
            )
            data["storage_path"] = key
            data["public_url"] = url
        elif is_created:
            data["storage_path"] = ""
            data["public_url"] = ""


class ExhibitMediaAdmin(ModelView, model=ExhibitMedia):
    name = "Exhibit Media"
    name_plural = "Exhibit Media"
    icon = "fa-solid fa-photo-film"
    column_list = [ExhibitMedia.exhibit, ExhibitMedia.public_url, ExhibitMedia.media_type, ExhibitMedia.is_cover, ExhibitMedia.id]
    column_labels = {
        "exhibit": "Exhibit", "storage_path": "File", "public_url": "Public URL",
        "media_type": "Type", "is_cover": "Cover", "sort_order": "Order",
    }
    form_overrides = {"storage_path": FileField}
    form_columns = ["exhibit", "storage_path", "media_type", "is_cover", "sort_order"]
    can_delete = True

    async def on_model_change(self, data, model, is_created, request):
        file = data.get("storage_path")
        if file and hasattr(file, "filename") and file.filename:
            content = await file.read()
            key, url = await asyncio.get_event_loop().run_in_executor(
                None, _upload_file, content, file.filename, "media"
            )
            data["storage_path"] = key
            data["public_url"] = url
        elif is_created:
            data["storage_path"] = ""
            data["public_url"] = ""



admin.add_view(CountryAdmin)
admin.add_view(CityAdmin)
admin.add_view(MuseumAdmin)
admin.add_view(HallAdmin)
admin.add_view(ExhibitAdmin)
admin.add_view(ExhibitTranslationAdmin)
admin.add_view(ExhibitMediaAdmin)
admin.add_view(ExhibitAudioTrackAdmin)
admin.add_view(UserAdmin)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, settings.BACKEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(museums_router, prefix="/api/v1")
app.include_router(exhibits_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
