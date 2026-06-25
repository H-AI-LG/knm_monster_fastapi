from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, select, func

from src.artifacts import service as artifacts_service
from src.artifacts.models import GameArtifact
from src.artifacts.schemas import ArtifactDetail, ArtifactSummary, QuizResponse
from src.database import get_db

from src.users.models import User
from src.users.constants import INTEREST_CHOICES

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=list[ArtifactSummary])
async def list_artifacts(
    zone: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactSummary]:
    return await artifacts_service.list_game_artifacts(zone, db)


ZONES = ["prehistory", "ancient", "sillaBalhae", "goryeo", "medieval"]

@router.get("/recommend/{user_id}", response_model=list[ArtifactSummary])
async def get_recommended_artifacts(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactSummary]:
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 30분→5개, 60분→10개, 90분→15개, 120분→20개
    user_view_time = user.view_time if user.view_time else 60
    total_limit = max(1, user_view_time // 6)

    # 관심사 키워드 수집
    keywords: list[str] = []
    if user.interests:
        for code in [c.strip() for c in user.interests.split(",") if c.strip()]:
            cat = next((c for c in INTEREST_CHOICES if c["code"] == code), None)
            if cat:
                keywords.extend(cat["keywords"])

    slots_per_zone = max(1, total_limit // len(ZONES))
    seen_ids: set[str] = set()
    artifacts: list[GameArtifact] = []

    for zone in ZONES:
        zone_picks: list[GameArtifact] = []

        # 1순위: 해당 zone + 관심사 키워드 매칭 (랜덤 순서)
        if keywords:
            kw_conditions = or_(*(
                or_(
                    GameArtifact.name.ilike(f"%{kw}%"),
                    GameArtifact.era.ilike(f"%{kw}%"),
                    GameArtifact.persona.ilike(f"%{kw}%"),
                    GameArtifact.greeting_fallback.ilike(f"%{kw}%"),
                )
                for kw in keywords
            ))
            rows = await db.execute(
                select(GameArtifact)
                .where(GameArtifact.zone == zone, kw_conditions)
                .order_by(func.random())
                .limit(slots_per_zone)
            )
            for a in rows.scalars():
                if a.id not in seen_ids:
                    zone_picks.append(a)
                    seen_ids.add(a.id)

        # 2순위: 해당 zone에서 키워드 무관하게 랜덤 (폴백)
        if len(zone_picks) < slots_per_zone:
            rows = await db.execute(
                select(GameArtifact)
                .where(
                    GameArtifact.zone == zone,
                    GameArtifact.id.notin_(seen_ids) if seen_ids else True,
                )
                .order_by(func.random())
                .limit(slots_per_zone - len(zone_picks))
            )
            for a in rows.scalars():
                if a.id not in seen_ids:
                    zone_picks.append(a)
                    seen_ids.add(a.id)

        artifacts.extend(zone_picks)
        if len(artifacts) >= total_limit:
            break

    # 3순위: zone 없는 유물 또는 부족한 슬롯 채우기 (랜덤)
    if len(artifacts) < total_limit:
        rows = await db.execute(
            select(GameArtifact)
            .where(GameArtifact.id.notin_(seen_ids) if seen_ids else True)
            .order_by(func.random())
            .limit(total_limit - len(artifacts))
        )
        artifacts.extend(rows.scalars().all())

    return [
        ArtifactSummary(
            id=a.id,
            number=a.number,
            name=a.name,
            grade=a.grade,
            era=a.era,
            image_key=a.image_key,
            zone=a.zone,
        )
        for a in artifacts[:total_limit]
    ]


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
    # 유저의 관심사 문자열을 분석하여 매칭할 한글 키워드 수집
    # target_keywords = []
    # if user.interests:
    #     user_code_list = user.interests.split(",")
    #     for choice in INTEREST_CHOICES:
    #         if choice["code"] in user_code_list:
    #             target_keywords.extend(choice["keywords"])
    
    # # 이미 검증된 artifacts_service.search 함수를 활용해 조회
    # artifacts = []
    # if target_keywords:
    #     seen_ids = set()
    #     seen_titles = set()
        
    #     for kw in target_keywords:
    #         search_results = await artifacts_service.search(kw, db)
            
    #         for a in search_results:
    #             if a.id in seen_ids or (a.title and a.title in seen_titles):
    #                 continue
                
    #             seen_ids.add(a.id)
    #             if a.title:
    #                 seen_titles.add(a.title)
                    
    #             artifacts.append(a)
                
    #         if len(artifacts) >= 10:
    #             artifacts = artifacts[:10]
    #             break
            
    # # 관심사가 없거나 검색 결과가 없다면 기본 유물 무작위 10개 노출
    # if not artifacts:
    #     artifacts = await artifacts_service.search("", db)
    
    #     unique_defaults =[]
    #     default_titles = set()
    #     for a in artifacts:
    #         if a.title not in default_titles:
    #             unique_defaults.append(a)
    #             default_titles.add(a.title)
    #     artifacts = unique_defaults[:10]
        
    # return [
    #     ArtifactSearchResponse(
    #         id=a.id,
    #         title=a.title or "",
    #         temporal=a.temporal or "",
    #         subdescription=a.subdescription or "",
    #         medium=a.medium or "",
    #     ) for a in artifacts
    # ]
                    
