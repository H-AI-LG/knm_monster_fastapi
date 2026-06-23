from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.models import CustomModel

class InterestChoiceResponse(BaseModel):
    code: str
    name: str

class FrontInterestItem(BaseModel):
    id: str = Field(..., description="프론트엔드 INTEREST_OPTIONS의 id (백엔드의 code와 매칭)")
    label: str = Field(..., description="프론트엔드 INTEREST_OPTIONS의 label (백엔드의 name과 매칭)")
    artifactTags: List[str] = Field(default=[], description="프론트엔드 INTEREST_OPTIONS의 artifactTags (백엔드의 keywords와 매칭)")

class LoginRequest(BaseModel):
    name: str = Field(..., description="학생 이름")
    parent_phone: str = Field(..., description="부모님 전화번호")
    parent_email: Optional[str] = Field(None, description="부모님 이메일 (선택)")
    interests: List[str] = Field(default=[], description="관심사 리스트")
    view_time: Optional[int] = Field(None, description="관람 시간(분)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "홍길동",
                "parent_phone": "010-1234-5678",
                "parent_email": "parents@email.com",
                "interests": ["craft", "warfare"],
                "view_time": 60
            }
        }
    )

class LoginResponse(BaseModel):
    message: str
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CollectArtifactRequest(CustomModel):
    artifact_id: str


class CollectArtifactResponse(CustomModel):
    artifact_id: str
    collected_at: datetime