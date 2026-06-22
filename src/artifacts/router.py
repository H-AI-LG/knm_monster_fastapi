from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.artifacts import service as artifacts_service
from src.artifacts.schemas import ArtifactDB, ArtifactSearchResponse
from src.database import get_db

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("/search", response_model=list[ArtifactSearchResponse])
async def search_artifacts(
    q: str,
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactSearchResponse]:
    artifacts = await artifacts_service.search(q, db)
    return [
        ArtifactSearchResponse(
            id=a.id,
            title=a.title or "",
            temporal=a.temporal or "",
            subdescription=a.subdescription or "",
            medium=a.medium or "",
        )
        for a in artifacts
    ]


@router.get("/{artifact_id}", response_model=ArtifactDB)
async def get_artifact(
    artifact_id: int,
    db: AsyncSession = Depends(get_db),
) -> ArtifactDB:
    artifact = await artifacts_service.get_by_id(artifact_id, db)
    return artifacts_service.to_schema(artifact)
