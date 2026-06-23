from src.exceptions import AppException


class UserNotFound(AppException):
    def __init__(self, user_id: int):
        super().__init__(status_code=404, detail=f"유저를 찾을 수 없습니다: {user_id}")


class ArtifactAlreadyCollected(AppException):
    def __init__(self, artifact_id: str):
        super().__init__(status_code=409, detail=f"이미 수집한 유물입니다: {artifact_id}")
