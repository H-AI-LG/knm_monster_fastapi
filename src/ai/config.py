from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    # Bedrock: AWS 자격증명은 환경변수(AWS_ACCESS_KEY_ID 등) 또는 ECS IAM Role로 자동 주입
    AWS_REGION: str = "ap-northeast-2"
    # 아시아 크로스리전 추론 프로파일 ID
    AI_MODEL: str = "ap.anthropic.claude-haiku-4-5-20251001-v1:0"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env", "extra": "ignore"}


ai_settings = AIConfig()
