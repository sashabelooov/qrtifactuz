from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.museum.router import router as museums_router
from sqladmin import Admin, ModelView
from app.models.user import User
from app.models.museum import Museum, Hall
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
    debug=settings.DEBUG,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.is_active, User.is_admin, User.created_at]
    column_searchable_list = [User.email]
    can_delete = True


class MuseumAdmin(ModelView, model=Museum):
    column_list = [Museum.id, Museum.name, Museum.slug, Museum.city, Museum.is_active]
    column_searchable_list = [Museum.name, Museum.slug]
    can_delete = True


class HallAdmin(ModelView, model=Hall):
    column_list = [Hall.id, Hall.name, Hall.museum_id, Hall.floor]
    can_delete = True



class ExhibitAdmin(ModelView, model=Exhibit):
    column_list = [Exhibit.id, Exhibit.slug, Exhibit.status, Exhibit.views_count, Exhibit.listens_count]
    column_searchable_list = [Exhibit.slug]
    can_delete = True


class ExhibitTranslationAdmin(ModelView, model=ExhibitTranslation):
    column_list = [ExhibitTranslation.id, ExhibitTranslation.exhibit_id, ExhibitTranslation.language, ExhibitTranslation.title]
    can_delete = True

class ExhibitAudioTrackAdmin(ModelView, model=ExhibitAudioTrack):
    column_list = [ExhibitAudioTrack.id, ExhibitAudioTrack.exhibit_id, ExhibitAudioTrack.language, ExhibitAudioTrack.public_url, ExhibitAudioTrack.duration_seconds]
    can_delete = True

class ExhibitMediaAdmin(ModelView, model=ExhibitMedia):
    column_list = [ExhibitMedia.id, ExhibitMedia.exhibit_id, ExhibitMedia.public_url, ExhibitMedia.is_cover]
    can_delete = True



admin.add_view(ExhibitTranslationAdmin)
admin.add_view(ExhibitAudioTrackAdmin)
admin.add_view(ExhibitMediaAdmin)



admin.add_view(ExhibitAdmin)
admin.add_view(UserAdmin)
admin.add_view(MuseumAdmin)
admin.add_view(HallAdmin)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(museums_router, prefix="/api/v1")
app.include_router(exhibits_router, prefix="/api/v1")
