from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environment-driven application settings for secure runtime configuration.
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    model_storage_path: str = Field(default="./models", alias="MODEL_STORAGE_PATH")
    voice_verification_threshold: float = Field(default=-50.0, alias="VOICE_VERIFICATION_THRESHOLD")
    allowed_origins: list[str] | str = Field(default="http://localhost:5173", alias="ALLOWED_ORIGINS")
    max_audio_duration_seconds: int = Field(default=10, alias="MAX_AUDIO_DURATION_SECONDS")
    min_audio_duration_seconds: int = Field(default=2, alias="MIN_AUDIO_DURATION_SECONDS")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, list):
            return value
        return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
