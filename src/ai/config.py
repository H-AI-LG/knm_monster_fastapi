from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    ANTHROPIC_API_KEY: str
    AI_MODEL: str = "claude-haiku-4-5-20251001"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env"}


ai_settings = AIConfig()
