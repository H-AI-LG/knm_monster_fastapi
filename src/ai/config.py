from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    # Bedrock: AWS 자격증명은 환경변수(AWS_ACCESS_KEY_ID 등) 또는 ECS IAM Role로 자동 주입
    AWS_REGION: str = "us-east-1"
    # 크로스리전 추론 프로파일 ID (Bedrock 콘솔에서 모델 액세스 활성화 필요)
    AI_MODEL: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    AI_MAX_TOKENS: int = 300

    model_config = {"env_file": ".env"}


ai_settings = AIConfig()
