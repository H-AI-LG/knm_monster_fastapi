from src.artifacts.schemas import ArtifactResponse
from src.artifacts.exceptions import ArtifactNotFound


async def list_artifacts() -> list[ArtifactResponse]:
    # TODO: DB 연동 (현재는 프론트엔드 artifacts.js 데이터를 그대로 사용)
    return []


async def get_artifact(artifact_id: str) -> ArtifactResponse:
    # TODO: DB 연동
    raise ArtifactNotFound(artifact_id)
