from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rnum: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    subdescription: Mapped[Optional[str]] = mapped_column(Text)   # 분류 카테고리
    temporal: Mapped[Optional[str]] = mapped_column(String(200))  # 시대
    spatial: Mapped[Optional[str]] = mapped_column(String(500))   # 국적/출토지
    medium: Mapped[Optional[str]] = mapped_column(String(500))    # 재질
    extent: Mapped[Optional[str]] = mapped_column(String(500))    # 크기
    subject_keyword: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[Optional[str]] = mapped_column(Text)
    local_id: Mapped[Optional[str]] = mapped_column(String(200))

    # Option C 업그레이드 시: pgvector 임베딩 컬럼 추가 예정
    # embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(1536))

    __table_args__ = (
        Index("ix_artifacts_title", "title"),
    )

# 게임 콘텐츠

class GameArtifact(Base):
    __tablename__ = "game_artifacts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    grade: Mapped[str | None] = mapped_column(String)
    era: Mapped[str | None] = mapped_column(String)
    persona: Mapped[str | None] = mapped_column(String)
    image_key: Mapped[str | None] = mapped_column(String)
    image_path: Mapped[str | None] = mapped_column(String)
    zone: Mapped[str | None] = mapped_column(String, index=True)
    greeting_fallback: Mapped[str | None] = mapped_column(Text)

    dialogues: Mapped[list[GameArtifactDialogue]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
        order_by="GameArtifactDialogue.sort_order",
    )
    quizzes: Mapped[list[GameArtifactQuiz]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
        order_by="GameArtifactQuiz.sort_order",
    )


class GameArtifactDialogue(Base):
    __tablename__ = "game_artifact_dialogues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("game_artifacts.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    artifact: Mapped[GameArtifact] = relationship(back_populates="dialogues")
    choices: Mapped[list[GameArtifactDialogueChoice]] = relationship(
        back_populates="dialogue",
        cascade="all, delete-orphan",
        order_by="GameArtifactDialogueChoice.sort_order",
    )


class GameArtifactDialogueChoice(Base):
    __tablename__ = "game_artifact_dialogue_choices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dialogue_id: Mapped[int] = mapped_column(
        ForeignKey("game_artifact_dialogues.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    dialogue: Mapped[GameArtifactDialogue] = relationship(back_populates="choices")


class GameArtifactQuiz(Base):
    __tablename__ = "game_artifact_quizzes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("game_artifacts.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False)
    answer_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    artifact: Mapped[GameArtifact] = relationship(back_populates="quizzes")