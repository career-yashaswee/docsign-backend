from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    PORT: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()
