from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "Real-Time Chat API"
    DEBUG: bool = False

    # Primary connection string (optional). If not set, the parts below will be composed.
    DATABASE_URL: Optional[str] = None

    # Fallback pieces to compose a DATABASE_URL when DATABASE_URL is not provided
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"

    # Returns an asyncpg-compatible SQLAlchemy URL. Prefers `DATABASE_URL`.
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB

        if user and password:
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

        # If user/password not provided, return host-only URL (useful for some local setups)
        return f"postgresql+asyncpg://{host}:{port}/{db}"


settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict



class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "Real-Time Chat API"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key"
    ALLOWED_HOSTS: list[str] = ["*"]
    API_VERSION: str = "/api/v1"