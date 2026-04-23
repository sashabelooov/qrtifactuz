import uuid
import asyncio
import boto3
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from markupsafe import Markup
from wtforms import FileField
from app.api.v1.museum.router import router as museums_router
from app.models.user import User
from app.models.museum import Country, City, Museum
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
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    openapi_tags=[],
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
        creds = settings.get_admin_credentials()
        username = form.get("username", "")
        password = form.get("password", "")
        if creds.get(username) == password:
            request.session.update({"admin": True, "admin_user": username})
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
    column_list = [User.email, User.is_active, User.is_admin]
    column_searchable_list = [User.email]
    column_labels = {"is_active": "Active", "is_admin": "Admin"}
    form_columns = ["email", "hashed_password", "is_active", "is_admin"]
    can_delete = True

    async def on_model_change(self, data, model, is_created, request):
        from app.core.security import hash_password
        password = data.get("hashed_password", "")
        if password and not password.startswith("$2b$"):
            data["hashed_password"] = hash_password(password)


class CountryAdmin(ModelView, model=Country):
    name = "Country"
    name_plural = "Countries"
    icon = "fa-solid fa-earth-asia"
    column_list = [Country.name, Country.code]
    column_searchable_list = [Country.name]
    form_excluded_columns = ["created_at", "cities"]
    can_delete = True


class CityAdmin(ModelView, model=City):
    name = "City"
    name_plural = "Cities"
    icon = "fa-solid fa-city"
    column_list = [City.name, City.country, City.created_at]
    column_searchable_list = [City.name]
    column_labels = {"country": "Country", "created_at": "Created"}
    form_excluded_columns = ["created_at", "museums"]
    can_delete = True


class MuseumAdmin(ModelView, model=Museum):
    name = "Museum"
    name_plural = "Museums"
    icon = "fa-solid fa-landmark"
    column_list = [Museum.name, Museum.slug, Museum.city_rel, Museum.is_active, Museum.created_at]
    column_details_list = ["name", "slug", "city_rel", "description", "address", "logo_url", "qr_code_url", "is_active", "created_at"]
    column_searchable_list = [Museum.name, Museum.slug]
    column_labels = {"city_rel": "City", "is_active": "Active", "created_at": "Created", "qr_code_url": "QR Code", "logo_url": "Logo"}
    column_formatters_detail = {
        "qr_code_url": lambda m, a: Markup(
            f'<img src="{m.qr_code_url}" style="width:180px;height:180px">'
        ) if m.qr_code_url else "Not generated yet",
    }
    form_excluded_columns = ["created_at", "updated_at", "city_rel", "exhibits", "qr_code_url"]
    can_delete = True

    async def after_model_change(self, data, model, is_created, request):
        if is_created:
            from app.tasks.qr_tasks import generate_museum_qr
            generate_museum_qr.delay(str(model.id), model.slug)



class ExhibitAdmin(ModelView, model=Exhibit):
    name = "Exhibit"
    name_plural = "Exhibits"
    icon = "fa-solid fa-image"
    column_list = [Exhibit.slug, Exhibit.status, Exhibit.views_count, Exhibit.listens_count]
    column_searchable_list = [Exhibit.slug]
    column_labels = {
        "museum": "Museum",
        "views_count": "Views", "listens_count": "Listens",
        "translations": "Translations",
    }
    column_details_list = ["museum", "slug", "status", "translations"]
    show_compact_lists = False
    column_formatters_detail = {}
    form_columns = ["museum", "slug", "status"]
    can_delete = True

    async def after_model_change(self, data, model, is_created, request):
        if is_created:
            from app.tasks.qr_tasks import generate_exhibit_qr
            generate_exhibit_qr.delay(str(model.id), model.slug)


class ExhibitTranslationAdmin(ModelView, model=ExhibitTranslation):
    name = "Translation"
    name_plural = "Translations"
    icon = "fa-solid fa-language"
    column_list = [ExhibitTranslation.exhibit, ExhibitTranslation.language, ExhibitTranslation.title]
    column_labels = {
        "exhibit": "Exhibit", "language": "Language", "title": "Title",
        "audio_url": "Audio", "media_url": "Image",
    }
    column_details_list = ["exhibit", "language", "title", "description", "audio_url", "media_url"]
    column_formatters_detail = {
        "audio_url": lambda m, a: Markup(
            f'<audio controls style="width:100%"><source src="{m.audio_url}" type="audio/mpeg">'
            f'<source src="{m.audio_url}" type="audio/mp4">'
            f'Your browser does not support audio.</audio>'
        ) if m.audio_url else "",
        "media_url": lambda m, a: Markup(
            f'<img src="{m.media_url}" style="max-width:400px;max-height:300px;border-radius:6px">'
        ) if m.media_url else "",
    }
    form_columns = ["exhibit", "language", "title", "description"]
    can_delete = True

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        form_class.audio_file = FileField("Audio File (mp3)")
        form_class.media_file = FileField("Media File (image/video)")
        return form_class

    column_default_sort = [("created_at", True)]

    async def on_model_change(self, data, model, is_created, request):
        from app.core.database import engine
        from sqlalchemy.ext.asyncio import AsyncSession
        form = await request.form()
        audio_file = data.pop("audio_file", None) or form.get("audio_file")
        media_file = data.pop("media_file", None) or form.get("media_file")

        # sqladmin puts the Exhibit ORM object in data["exhibit"], not data["exhibit_id"]
        exhibit_id = data.get("exhibit_id") or getattr(model, "exhibit_id", None)
        if not exhibit_id:
            exhibit_obj = data.get("exhibit") or getattr(model, "exhibit", None)
            if exhibit_obj is not None:
                exhibit_id = getattr(exhibit_obj, "id", None)

        language = data.get("language") or getattr(model, "language", None)
        if hasattr(language, "value"):
            language = language.value

        if audio_file and hasattr(audio_file, "filename") and audio_file.filename and exhibit_id:
            content = await audio_file.read()
            key, url = await asyncio.get_event_loop().run_in_executor(
                None, _upload_file, content, audio_file.filename, "audio"
            )
            data["audio_url"] = url
            model.audio_url = url
            async with AsyncSession(engine) as session:
                track = ExhibitAudioTrack(
                    exhibit_id=exhibit_id, language=language,
                    storage_path=key, public_url=url,
                )
                session.add(track)
                await session.commit()

        if media_file and hasattr(media_file, "filename") and media_file.filename and exhibit_id:
            content = await media_file.read()
            key, url = await asyncio.get_event_loop().run_in_executor(
                None, _upload_file, content, media_file.filename, "media"
            )
            data["media_url"] = url
            model.media_url = url
            async with AsyncSession(engine) as session:
                media = ExhibitMedia(
                    exhibit_id=exhibit_id, storage_path=key,
                    public_url=url, media_type="image", is_cover=False, sort_order=0,
                )
                session.add(media)
                await session.commit()


class ExhibitAudioTrackAdmin(ModelView, model=ExhibitAudioTrack):
    name = "Audio Track"
    name_plural = "Audio Tracks"
    icon = "fa-solid fa-headphones"

    def is_visible(self, request) -> bool:
        return False
    column_list = [ExhibitAudioTrack.exhibit, ExhibitAudioTrack.language, ExhibitAudioTrack.duration_seconds]
    column_details_list = ["exhibit", "language", "public_url", "duration_seconds"]
    column_labels = {
        "exhibit": "Exhibit", "language": "Language",
        "storage_path": "File", "public_url": "Audio", "duration_seconds": "Duration (sec)",
    }
    column_formatters_detail = {
        "public_url": lambda m, a: Markup(
            f'<audio controls style="width:100%"><source src="{m.public_url}" type="audio/mpeg">'
            f'<source src="{m.public_url}" type="audio/mp4">'
            f'<source src="{m.public_url}" type="audio/ogg">Your browser does not support audio.</audio>'
        ) if m.public_url else "",
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

    def is_visible(self, request) -> bool:
        return False
    column_list = [ExhibitMedia.exhibit, ExhibitMedia.media_type, ExhibitMedia.is_cover, ExhibitMedia.sort_order]
    column_details_list = ["exhibit", "public_url", "media_type", "is_cover", "sort_order"]
    column_labels = {
        "exhibit": "Exhibit", "storage_path": "File",
        "public_url": "Preview", "media_type": "Type", "is_cover": "Cover", "sort_order": "Order",
    }
    column_formatters_detail = {
        "public_url": lambda m, a: Markup(
            f'<img src="{m.public_url}" style="max-width:400px;max-height:300px;border-radius:6px">'
        ) if m.public_url and m.media_type == "image" else Markup(
            f'<video controls style="max-width:400px"><source src="{m.public_url}"></video>'
        ) if m.public_url else "",
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


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
