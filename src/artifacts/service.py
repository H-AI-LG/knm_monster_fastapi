from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.artifacts.exceptions import ArtifactNotFound
from src.artifacts.models import Artifact, GameArtifact, GameArtifactDialogue, GameArtifactQuiz
from src.artifacts.schemas import ArtifactDB


async def get_by_name(name: str, db: AsyncSession) -> Artifact:
    result = await db.execute(
        select(Artifact).where(Artifact.title == name).limit(1)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise ArtifactNotFound(name)
    return artifact


def to_schema(artifact: Artifact) -> ArtifactDB:
    return ArtifactDB(
        id=artifact.id,
        title=artifact.title or "",
        description=artifact.description or "",
        subdescription=artifact.subdescription or "",
        temporal=artifact.temporal or "",
        spatial=artifact.spatial or "",
        medium=artifact.medium or "",
        extent=artifact.extent or "",
        url=artifact.url or "",
    )


async def list_game_artifacts(zone: str | None, db: AsyncSession) -> list[GameArtifact]:
    stmt = select(GameArtifact)
    if zone:
        stmt = stmt.where(GameArtifact.zone == zone)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_game_artifact(artifact_id: str, db: AsyncSession) -> GameArtifact:
    stmt = (
        select(GameArtifact)
        .where(GameArtifact.id == artifact_id)
        .options(
            selectinload(GameArtifact.dialogues).selectinload(GameArtifactDialogue.choices)
        )
    )
    result = await db.execute(stmt)
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise ArtifactNotFound(artifact_id)
    return artifact


async def list_quizzes(artifact_id: str, db: AsyncSession) -> list[GameArtifactQuiz]:
    exists = await db.get(GameArtifact, artifact_id)
    if not exists:
        raise ArtifactNotFound(artifact_id)
    result = await db.execute(
        select(GameArtifactQuiz)
        .where(GameArtifactQuiz.artifact_id == artifact_id)
        .order_by(GameArtifactQuiz.sort_order)
    )
    return list(result.scalars().all())
