from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database.db import get_db
from app.models.schemas import LoginResponse, RefreshRequest, RegisterResponse, VerifyResponse
from app.services.auth_service import get_verified_user, login_user, refresh_access_token, register_user
from app.utils.rate_limit import limiter
from app.utils.security import get_bearer_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(
    username: str = Form(...),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RegisterResponse:
    user_id = await register_user(db, username, audio_file, settings)
    return RegisterResponse(user_id=user_id, message="Voice registered successfully")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    # Request is required by slowapi for per-IP rate limiting.
    _ = request
    access_token, refresh_token = await login_user(db, username, audio_file, settings)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    access_token = await refresh_access_token(db, payload.refresh_token, settings)
    return LoginResponse(access_token=access_token, refresh_token=payload.refresh_token)


@router.get("/verify", response_model=VerifyResponse)
async def verify(
    token: str = Depends(get_bearer_token),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> VerifyResponse:
    user = await get_verified_user(db, token, settings)
    return VerifyResponse(user_id=user.id, username_fingerprint=user.username_fingerprint, verified=True)
