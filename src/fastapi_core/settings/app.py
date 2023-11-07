from pydantic_settings import BaseSettings


class APPSettings(BaseSettings):
    APP_NAME: str = "Service API"
    API_VERSION: str = "production"

    API_DESCRIPTION: str | None

    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_ORIGINS: list[str] = ["*"]
