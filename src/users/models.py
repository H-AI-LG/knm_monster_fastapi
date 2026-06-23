from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.artifacts.models import UserArtifact

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)          # 학생 이름
    parent_phone: Mapped[str] = mapped_column(String(50), nullable=False)   # 부모님 전화번호
    interests: Mapped[Optional[str]] = mapped_column(String(500))             # 관심사 (ex: "도자기, 전쟁, 장신구")
    view_time: Mapped[Optional[int]] = mapped_column(Integer)
    
    collected_artifacts: Mapped[list[UserArtifact]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_name", "name"),
        Index("ix_users_parent_phone", "parent_phone"),
    )