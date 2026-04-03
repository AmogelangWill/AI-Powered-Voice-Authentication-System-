import io
import math
import wave

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import Settings
from app.database.db import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_voiceauth.db"


def _test_settings() -> Settings:
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET_KEY="test-secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
        REFRESH_TOKEN_EXPIRE_DAYS=7,
        MODEL_STORAGE_PATH="./models",
        VOICE_VERIFICATION_THRESHOLD=-500.0,
        ALLOWED_ORIGINS="http://localhost:5173",
        MAX_AUDIO_DURATION_SECONDS=10,
        MIN_AUDIO_DURATION_SECONDS=2,
        ENVIRONMENT="test",
    )


@pytest.fixture(scope="session")
def sine_wave_wav_bytes() -> bytes:
    sample_rate = 16000
    duration = 3.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = (0.2 * np.sin(2 * math.pi * 220 * t) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(tone.tobytes())
    return buffer.getvalue()


@pytest.fixture(scope="session")
def short_wav_bytes() -> bytes:
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = (0.2 * np.sin(2 * math.pi * 220 * t) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(tone.tobytes())
    return buffer.getvalue()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture()
def client(monkeypatch):
    test_settings = _test_settings()
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with session_local() as session:
            yield session

    monkeypatch.setattr("app.config.get_settings", lambda: test_settings)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
