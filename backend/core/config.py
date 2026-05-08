from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./pcm.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: str = "PCM Sistema de Manutenção"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    APP_NAME: str = "PCM - Controle de Manutenção"
    FRONTEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
