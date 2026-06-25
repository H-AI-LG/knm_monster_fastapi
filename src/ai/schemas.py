from __future__ import annotations

from typing import Optional

from src.models import CustomModel
from src.ai.constants import STAGE_GREETING


class ChatRequest(CustomModel):
    artifact_id: str        # 게임 내부 ID (artifact_001 등)
    artifact_name: str      # 한국어 유물명 — DB 조회 키 (예: "주먹도끼")
    message: str
    stage: str = STAGE_GREETING  # greeting | dialogue | quiz | praise


class ChatResponse(CustomModel):
    reply: str
    score: Optional[float] = None  # 칭찬 배틀 점수 0.0~1.0, 다른 단계는 None


class PraiseRequest(CustomModel):
    artifact_ids: list[str]  # TOP3 유물 ID
    praise_text: str          # 유저가 입력한 칭찬 텍스트


class PraiseResponse(CustomModel):
    score: float       # 0.0~1.0 (보스 대미지 배율로 사용)
    feedback: str      # AI가 분석한 피드백 텍스트


# ── 카드 등급 채점 (TOP3 개별 채점) ────────────────────────────────

class PraiseItem(CustomModel):
    artifact_id: str    # artifact_001 등
    artifact_name: str  # 한국어 유물명
    era: str            # 시대 (예: 신라)
    praise_text: str    # 유저가 입력한 칭찬


class PraiseItemResult(CustomModel):
    artifact_id: str
    grade: str          # common | rare | legendary
    score: float        # 0.0~1.0
    feedback: str       # AI 한 줄 칭찬 피드백


class PraiseScoreRequest(CustomModel):
    praises: list[PraiseItem]


class PraiseScoreResponse(CustomModel):
    results: list[PraiseItemResult]
