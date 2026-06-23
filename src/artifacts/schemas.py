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


class DialogueChoice(CustomModel):
    text: str
    answer: str


class Dialogue(CustomModel):
    question: str
    choices: list[DialogueChoice]


class ArtifactSummary(CustomModel):
    id: str
    number: str
    name: str
    grade: str | None = None
    era: str | None = None
    image_key: str | None = None
    zone: str | None = None


class ArtifactDetail(ArtifactSummary):
    persona: str | None = None
    image_path: str | None = None
    greeting_fallback: str | None = None
    dialogues: list[Dialogue] = []


class QuizResponse(CustomModel):
    id: int
    question: str
    options: list[str]
    answer_index: int
    explanation: str | None = None
