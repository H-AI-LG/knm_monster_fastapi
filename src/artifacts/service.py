from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.artifacts.exceptions import ArtifactNotFound
from src.artifacts.models import Artifact
from src.artifacts.schemas import ArtifactDB


async def get_by_name(name: str, db: AsyncSession) -> Artifact:
    result = await db.execute(
        select(Artifact).where(Artifact.title == name).limit(1)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise ArtifactNotFound(name)
    return artifact


async def search(query: str, db: AsyncSession, limit: int = 10) -> list[Artifact]:
    result = await db.execute(
        select(Artifact)
        .where(Artifact.title.ilike(f"%{query}%"))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_id(artifact_id: int, db: AsyncSession) -> Artifact:
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise ArtifactNotFound(str(artifact_id))
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
