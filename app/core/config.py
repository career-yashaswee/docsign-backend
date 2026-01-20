from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    PORT: int = 8080
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/docsign"

    class Config:
        env_file = ".env"


settings = Settings()
