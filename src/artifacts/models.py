from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rnum: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    subdescription: Mapped[str | None] = mapped_column(Text)   # 분류 카테고리
    temporal: Mapped[str | None] = mapped_column(String(200))  # 시대
    spatial: Mapped[str | None] = mapped_column(String(500))   # 국적/출토지
    medium: Mapped[str | None] = mapped_column(String(500))    # 재질
    extent: Mapped[str | None] = mapped_column(String(500))    # 크기
    subject_keyword: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(Text)
    local_id: Mapped[str | None] = mapped_column(String(200))

    # Option C 업그레이드 시: pgvector 임베딩 컬럼 추가 예정
    # embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))

    __table_args__ = (
        Index("ix_artifacts_title", "title"),
    )
