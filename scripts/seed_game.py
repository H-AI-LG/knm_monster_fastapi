"""게임 유물 데이터 시드 스크립트.

Usage:
    python scripts/seed_game.py
    python scripts/seed_game.py --reset   # 기존 데이터 삭제 후 재시드
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.artifacts.models import (
    GameArtifact,
    GameArtifactDialogue,
    GameArtifactDialogueChoice,
    GameArtifactQuiz,
)
from src.config import settings
from src.database import Base

DATA_PATH = Path(__file__).parent.parent / "src" / "data" / "seed_data.json"

# artifact_id → zone 매핑
ZONE_MAP: dict[str, str] = {
    "artifact_001": "prehistory",
    "artifact_002": "prehistory",
    "artifact_003": "prehistory",
    "artifact_031": "prehistory",
    "artifact_032": "prehistory",
    "artifact_033": "prehistory",
    "artifact_034": "prehistory",
    "artifact_035": "prehistory",
    "artifact_036": "prehistory",
    "artifact_037": "prehistory",
    "artifact_038": "prehistory",
    "artifact_039": "prehistory",
    "artifact_040": "prehistory",
    "artifact_041": "prehistory",
    "artifact_042": "prehistory",
    "artifact_043": "prehistory",
    "artifact_044": "prehistory",
    "artifact_045": "prehistory",
    "artifact_046": "prehistory",
    "artifact_005": "ancient",
    "artifact_006": "ancient",
    "artifact_007": "ancient",
    "artifact_008": "ancient",
    "artifact_010": "medieval",
    "artifact_013": "medieval",
    "artifact_015": "medieval",
    "artifact_024": "medieval",
}


async def seed(session: AsyncSession, *, reset: bool = False) -> None:
    if reset:
        await session.execute(delete(GameArtifact))
        await session.commit()
        print("기존 데이터 삭제 완료.")
    else:
        result = await session.execute(select(GameArtifact).limit(1))
        if result.scalar_one_or_none():
            print("이미 시드 데이터가 존재합니다. --reset 옵션으로 재시드하세요.")
            return

    data: dict = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for artifact_id, a in data.items():
        artifact = GameArtifact(
            id=a["id"],
            number=a["number"],
            name=a["name"],
            grade=a.get("grade"),
            era=a.get("era"),
            persona=a.get("persona"),
            image_key=a.get("imageKey"),
            image_path=a.get("image"),
            zone=ZONE_MAP.get(artifact_id),
            greeting_fallback=a.get("greeting"),
        )

        for d_i, d in enumerate(a.get("dialogues", [])):
            dialogue = GameArtifactDialogue(
                question=d["question"],
                sort_order=d_i,
            )
            for c_i, c in enumerate(d["choices"]):
                dialogue.choices.append(
                    GameArtifactDialogueChoice(
                        text=c["text"],
                        answer=c["answer"],
                        sort_order=c_i,
                    )
                )
            artifact.dialogues.append(dialogue)

        for q_i, q in enumerate(a.get("quizzes", [])):
            artifact.quizzes.append(
                GameArtifactQuiz(
                    question=q["question"],
                    options=q["options"],
                    answer_index=q["answer"],
                    explanation=q.get("explanation"),
                    sort_order=q_i,
                )
            )

        session.add(artifact)

    await session.commit()
    print(f"[완료] {len(data)}개 유물 시드 완료.")


async def main(reset: bool) -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        await seed(session, reset=reset)
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="기존 데이터 삭제 후 재시드")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
