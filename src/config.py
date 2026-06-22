from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://d1y9mblfv6hml0.cloudfront.net",
        "https://knm.ai.kr",
    ]
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/knm"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Config()
