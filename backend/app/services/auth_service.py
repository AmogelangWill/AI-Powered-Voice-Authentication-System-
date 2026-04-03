from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.database.user_model import User, VoicePrint
from app.services.audio import read_and_preprocess_audio
from app.services.features import extract_frame_features
from app.services.model import get_model_path, load_gmm, save_gmm, score_gmm, train_gmm
from app.utils.exceptions import bad_request, unauthorized
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    fingerprint_username,
    hash_username,
    verify_username,
)


async def register_user(db: AsyncSession, username: str, audio_file, settings: Settings) -> int:
    if not username.strip():
        raise bad_request("Username is required")

    fingerprint = fingerprint_username(username)
    existing = await db.scalar(select(User).where(User.username_fingerprint == fingerprint))
    if existing:
        raise bad_request("User already exists")

    y, sr = await read_and_preprocess_audio(
        audio_file,
        min_duration_seconds=settings.min_audio_duration_seconds,
        max_duration_seconds=settings.max_audio_duration_seconds,
    )
    feature_matrix = extract_frame_features(y, sr)
    model = train_gmm(feature_matrix)

    user = User(username_hash=hash_username(username), username_fingerprint=fingerprint)
    db.add(user)
    await db.flush()

    model_path = get_model_path(settings.model_storage_path, user.id)
    save_gmm(model, model_path)

    db.add(VoicePrint(user_id=user.id, model_path=str(model_path)))
    await db.commit()
    await db.refresh(user)
    return user.id


async def login_user(db: AsyncSession, username: str, audio_file, settings: Settings) -> tuple[str, str]:
    fingerprint = fingerprint_username(username)
    user = await db.scalar(select(User).where(User.username_fingerprint == fingerprint))
    if not user or not verify_username(username, user.username_hash):
        raise unauthorized("Voice verification failed")

    voiceprint = await db.scalar(select(VoicePrint).where(VoicePrint.user_id == user.id))
    if not voiceprint:
        raise unauthorized("Voice verification failed")

    y, sr = await read_and_preprocess_audio(
        audio_file,
        min_duration_seconds=settings.min_audio_duration_seconds,
        max_duration_seconds=settings.max_audio_duration_seconds,
    )
    feature_matrix = extract_frame_features(y, sr)
    model = load_gmm(get_model_path(settings.model_storage_path, user.id))
    score = score_gmm(model, feature_matrix)

    if score < settings.voice_verification_threshold:
        raise unauthorized("Voice verification failed")

    access_token = create_access_token(user.id, settings)
    refresh_token = create_refresh_token(user.id, settings)
    return access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str, settings: Settings) -> str:
    payload = decode_token(refresh_token, expected_type="refresh", settings=settings)
    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    if not user:
        raise unauthorized("Invalid refresh token")
    return create_access_token(user_id, settings)


async def get_verified_user(db: AsyncSession, token: str, settings: Settings) -> User:
    payload = decode_token(token, expected_type="access", settings=settings)
    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    if not user:
        raise unauthorized("User not found")
    return user
