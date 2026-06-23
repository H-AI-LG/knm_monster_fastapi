from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.artifacts import service as artifacts_service
from src.artifacts.schemas import ArtifactDetail, ArtifactSummary, QuizResponse
from src.database import get_db

router = APIRouter(prefix="/artifact", tags=["artifact"])


@router.get("", response_model=list[ArtifactSummary])
async def list_artifacts(
    zone: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactSummary]:
    return await artifacts_service.list_game_artifacts(zone, db)


@router.get("/{artifact_id}", response_model=ArtifactDetail)
async def get_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
) -> ArtifactDetail:
    return await artifacts_service.get_game_artifact(artifact_id, db)


@router.get("/{artifact_id}/quizzes", response_model=list[QuizResponse])
async def list_quizzes(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[QuizResponse]:
    return await artifacts_service.list_quizzes(artifact_id, db)
