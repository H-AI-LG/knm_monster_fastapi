from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    AWS_REGION: str = "ap-northeast-2"
    # Bedrock 모델 ID (boto3 Converse API 형식)
    AI_MODEL: str = "anthropic.claude-3-5-haiku-20241022-v1:0"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env", "extra": "ignore"}


ai_settings = AIConfig()
