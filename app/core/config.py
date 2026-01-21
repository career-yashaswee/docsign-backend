from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    PORT: int = 8080
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/docsign"
    JWT_SECRET_KEY: str | None = "verystrong"

    UPLOAD_DIR: str = "data/uploads"
    MAX_CONTENT_LENGTH_MB: int = 20
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg", "docx"]

    class Config:
        env_file = ".env"


settings = Settings()
