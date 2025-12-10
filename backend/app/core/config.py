from typing import Optional
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

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
    POSTGRES_DB: str = "chat_db"
    
    #JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_TOKEN_AVAILABILITY_MIN: int 
    REFRESH_TOKEN_AVAILABILITY_MIN: int 
    
    #GOOGLE AUTH
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_SCOPES: str
    
    FRONTEND_URL: str
    BACKEND_URL: str
    ALLOWED_ORIGINS: str
    
    #FRONTED
    VITE_GOOGLE_CLIENT_ID: str
    VITE_API_URL: str

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
