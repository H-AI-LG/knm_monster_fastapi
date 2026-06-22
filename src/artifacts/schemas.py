from __future__ import annotations

from src.models import CustomModel


# DB에서 읽어온 유물 데이터 (내부용)
class ArtifactDB(CustomModel):
    id: int
    title: str
    description: str
    subdescription: str  # 분류 카테고리
    temporal: str        # 시대
    spatial: str         # 국적/출토지
    medium: str          # 재질
    extent: str          # 크기
    url: str


# API 응답용
class ArtifactSearchResponse(CustomModel):
    id: int
    title: str
    temporal: str
    subdescription: str
    medium: str
