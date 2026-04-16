import secrets
import httpx
from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.models.profile import Profile
from app.services.otp import get_redis


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
STATE_TTL = 600  # 10 minutes


async def get_google_auth_url() -> str:
    state = secrets.token_urlsafe(32)
    r = await get_redis()
    await r.set(f"oauth_state:{state}", "1", ex=STATE_TTL)
    await r.aclose()
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def validate_oauth_state(state: str) -> bool:
    r = await get_redis()
    value = await r.get(f"oauth_state:{state}")
    await r.delete(f"oauth_state:{state}")
    await r.aclose()
    return value is not None


async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        response.raise_for_status()
        return response.json()["access_token"]


async def get_google_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()



async def google_login(db: AsyncSession, user_info: dict) -> dict:
    google_id = user_info["id"]
    email = user_info["email"]

    # Try find by google_id first
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        # Try find by email (user registered with password before)
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            # Link google_id to existing account
            user.google_id = google_id
            user.is_active = True
        else:
            # Brand new user
            user = User(
                email=email,
                google_id=google_id,
                is_active=True,
            )
            db.add(user)
            await db.flush()

            profile = Profile(user_id=user.id)
            db.add(profile)

    await db.commit()
    await db.refresh(user)

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }
