from datetime import UTC, datetime, timedelta
import hashlib

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import Settings, get_settings
from app.utils.exceptions import unauthorized


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_username(username: str) -> str:
    return pwd_context.hash(username.strip().lower())


def verify_username(username: str, hashed: str) -> bool:
    return pwd_context.verify(username.strip().lower(), hashed)


def fingerprint_username(username: str) -> str:
    normalized = username.strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _create_token(subject: str, token_type: str, expires_delta: timedelta, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int, settings: Settings) -> str:
    return _create_token(str(user_id), "access", timedelta(minutes=settings.access_token_expire_minutes), settings)


def create_refresh_token(user_id: int, settings: Settings) -> str:
    return _create_token(str(user_id), "refresh", timedelta(days=settings.refresh_token_expire_days), settings)


def decode_token(token: str, expected_type: str, settings: Settings) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise unauthorized("Invalid token") from exc
    if payload.get("type") != expected_type:
        raise unauthorized("Invalid token type")
    return payload


def get_bearer_token(token: str = Depends(oauth2_scheme)) -> str:
    return token
