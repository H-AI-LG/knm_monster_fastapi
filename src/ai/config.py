from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    AWS_REGION: str = "ap-northeast-2"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    # Bedrock 모델 ID (boto3 Converse API 형식)
    AI_MODEL: str = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env", "extra": "ignore"}


ai_settings = AIConfig()
