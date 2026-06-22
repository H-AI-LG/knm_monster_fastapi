from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    AWS_REGION: str = "ap-northeast-2"
    # Bedrock API 키 방식 (IAM 불필요) — Bedrock 콘솔 > API 키에서 발급
    BEDROCK_API_KEY: str = ""
    # 모델 ID: Anthropic 형식 사용
    AI_MODEL: str = "claude-3-5-haiku-20241022"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env", "extra": "ignore"}


ai_settings = AIConfig()
