from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, select

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


@router.get("/recommend/{user_id}", response_model=list[ArtifactSummary])
async def get_recommended_artifacts(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactSummary]:
    ### 사용자 관심사 기반 맞춤형 유물 추천 API(최대 10개)
    
    # 로그인한 유저의 정보와 관심사 가져오기
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # (30분 -> 5개, 60분 -> 10개, 90분 -> 15개, 120분 -> 20개)
    user_view_time = user.view_time if user.view_time else 60
    total_limit = max(10, (user_view_time // 6))
    
    artifacts: list[GameArtifact] = []
    
    if user.interests:
        user_code_list = [c.strip() for c in user.interests.split(",") if c.strip()]
        num_categories = len(user_code_list)
        
        # 카테고리당 가져올 목표 개수 계산
        limit_per_category = max(1, total_limit // num_categories) if num_categories > 0 else total_limit
        
        seen_ids: set[str] = set()
        seen_names: set[str] = set()
        
        for code in user_code_list:
            # 현재 코드에 해당하는 카테고리 찾기
            category_info = next((c for c in INTEREST_CHOICES if c["code"] == code), None)
            if not category_info:
                continue
                
            category_artifacts_count = 0
            
            # 해당 카테고리 안의 키워드들 돌기
            for kw in category_info["keywords"]:
                search_pattern = f"%{kw}%"
                search_result = await db.execute(
                    select(GameArtifact)
                    .where(
                        or_(
                            GameArtifact.name.ilike(search_pattern),
                            GameArtifact.era.ilike(search_pattern),
                            GameArtifact.persona.ilike(search_pattern),
                            GameArtifact.greeting_fallback.ilike(search_pattern),
                            GameArtifact.zone.ilike(search_pattern),
                        )
                    )
                    .order_by(GameArtifact.number)
                    .limit(total_limit)
                )
                search_results = search_result.scalars().all()
                
                for a in search_results:
                    if a.id in seen_ids or (a.name and a.name in seen_names):
                        continue
                        
                    seen_ids.add(a.id)
                    if a.name:
                        seen_names.add(a.name)
                        
                    artifacts.append(a)
                    category_artifacts_count += 1
                    
                    # 현재 카테고리에서 목표한 개수를 채웠으면 루프 탈출
                    if category_artifacts_count >= limit_per_category:
                        break
                        
                if category_artifacts_count >= limit_per_category:
                    break
                    
            # 전체 10개가 다 채워졌다면 최종 종료
            if len(artifacts) >= total_limit:
                break

    # 4. 관심사가 없거나 검색 결과가 총 10개가 안 된다면 기본 유물로 잔여석 채우기
    if len(artifacts) < total_limit:
        default_result = await db.execute(
            select(GameArtifact)
            .order_by(GameArtifact.number)
            .limit(total_limit * 2)
        )
        default_results = default_result.scalars().all()

        for a in default_results:
            if len(artifacts) >= total_limit:
                break
            # 중복 검사
            if a.id not in [art.id for art in artifacts] and (not a.name or a.name not in [art.name for art in artifacts]):
                artifacts.append(a)
                

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
                    
