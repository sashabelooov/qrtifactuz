from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.google_auth import get_google_auth_url, exchange_code_for_token, get_google_user_info, google_login, validate_oauth_state
from app.core.exceptions import UnauthorizedException
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse, VerifyEmailRequest
from app.services.auth import login_user, refresh_tokens, register_user, verify_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account. A 6-digit OTP code is sent to the provided email. The account is not active until the email is verified via `/auth/verify-email`.",
)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(db, body.email, body.password)


@router.post(
    "/verify-email",
    response_model=TokenResponse,
    summary="Verify email with OTP",
    description="Verifies the user's email using the 6-digit OTP sent during registration. Returns access and refresh tokens on success. The account becomes active after this step.",
)
async def verify_email_route(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await verify_email(db, body.email, body.otp)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticates a user with email and password. Returns access token (valid 60 min) and refresh token (valid 30 days). Use the access token in the `Authorization: Bearer <token>` header for protected endpoints.",
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(db, body.email, body.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Issues a new access token using a valid refresh token. Use this when the access token expires. Returns a new access token and refresh token pair.",
)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(db, body.refresh_token)


@router.post(
    "/logout",
    status_code=204,
    summary="Logout current user",
    description="Logs out the currently authenticated user. Requires a valid access token in the Authorization header.",
)
async def logout(current_user=Depends(get_current_user)):
    return None


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    description="Returns the authenticated user's account information including email, admin status, and account state. Requires a valid access token.",
)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.get(
    "/google",
    summary="Start Google OAuth login",
    description="Returns a Google OAuth2 authorization URL. Redirect the user to `redirect_url` to begin the Google sign-in flow.",
)
async def google_auth():
    return {"redirect_url": await get_google_auth_url()}


@router.get(
    "/google/callback",
    summary="Google OAuth callback",
    description="Handles the OAuth2 callback from Google. Exchanges the authorization code for tokens, finds or creates the user, and redirects to the frontend with access and refresh tokens in the URL fragment.",
)
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if not await validate_oauth_state(state):
        raise UnauthorizedException("Invalid or expired OAuth state")

    access_token = await exchange_code_for_token(code)
    user_info = await get_google_user_info(access_token)
    tokens = await google_login(db, user_info)

    # Use URL fragment (#) — never sent to servers, never logged by proxies
    fragment = f"access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth.html#{fragment}")
