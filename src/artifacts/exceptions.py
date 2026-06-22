from src.exceptions import AppException


class ArtifactNotFound(AppException):
    def __init__(self, artifact_id: str):
        super().__init__(status_code=404, detail=f"유물을 찾을 수 없습니다: {artifact_id}")
