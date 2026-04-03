from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.config import get_settings
from app.database.db import init_db
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.utils.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup initializes database metadata for non-migration environments.
    await init_db()
    yield


settings = get_settings()
app = FastAPI(title="Voiceprint Authentication API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
