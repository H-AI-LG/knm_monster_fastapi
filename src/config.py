from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "https://d1y9mblfv6hml0.cloudfront.net",
        "https://knm.ai.kr",
    ]

    model_config = {"env_file": ".env"}


settings = Config()
