"""
국립중앙박물관 CSV 데이터를 PostgreSQL에 임포트합니다.

사용법:
    python scripts/seed.py --csv /path/to/유물정보.csv
    python scripts/seed.py --csv /path/to/유물정보.csv --batch-size 500
"""

import argparse
import asyncio
import csv
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artifacts.models import Artifact
import src.users.models
from src.database import Base
from src.users.models import User

def parse_row(row: dict) -> dict:
    return {
        "rnum": int(row["RNUM"]) if row.get("RNUM", "").strip().isdigit() else None,
        "title": row.get("TITLE", "").strip() or None,
        "description": row.get("DESCRIPTION", "").strip() or None,
        "subdescription": row.get("SUBDESCRIPTION", "").strip() or None,
        "temporal": row.get("TEMPORAL", "").strip() or None,
        "spatial": row.get("SPATIAL", "").strip() or None,
        "medium": row.get("MEDIUM", "").strip() or None,
        "extent": row.get("EXTENT", "").strip() or None,
        "subject_keyword": row.get("SUBJECTKEYWORD", "").strip() or None,
        "url": row.get("URL", "").strip() or None,
        "local_id": row.get("LOCALID", "").strip() or None,
    }


async def seed(csv_path: str, database_url: str, batch_size: int = 500) -> None:
    engine = create_async_engine(database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    total = 0
    batch: list[dict] = []

    async with SessionLocal() as session:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch.append(parse_row(row))
                if len(batch) >= batch_size:
                    session.add_all([Artifact(**r) for r in batch])
                    await session.commit()
                    total += len(batch)
                    print(f"\r{total:,}행 임포트 완료...", end="", flush=True)
                    batch.clear()

            if batch:
                session.add_all([Artifact(**r) for r in batch])
                await session.commit()
                total += len(batch)

    await engine.dispose()
    print(f"\n✅ 완료: 총 {total:,}행 임포트")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV 파일 경로")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument(
        "--db",
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/knm",
        help="DATABASE_URL",
    )
    args = parser.parse_args()

    asyncio.run(seed(args.csv, args.db, args.batch_size))
