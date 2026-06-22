from fastapi import APIRouter

from src.artifacts.schemas import ArtifactResponse
from src.artifacts import service as artifacts_service

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=list[ArtifactResponse])
async def list_artifacts() -> list[ArtifactResponse]:
    return await artifacts_service.list_artifacts()


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str) -> ArtifactResponse:
    return await artifacts_service.get_artifact(artifact_id)
