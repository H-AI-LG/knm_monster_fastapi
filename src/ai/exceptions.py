from src.exceptions import AppException


class AIServiceError(AppException):
    def __init__(self, detail: str = "AI 서비스 오류가 발생했습니다"):
        super().__init__(status_code=503, detail=detail)


class InvalidStageError(AppException):
    def __init__(self, stage: str):
        super().__init__(status_code=400, detail=f"유효하지 않은 대화 단계입니다: {stage}")
