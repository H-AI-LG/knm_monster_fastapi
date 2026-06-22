from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class LoginRequest(BaseModel):
    name: str = Field(..., description="학생 이름")
    parent_phone: str = Field(..., description="부모님 전화번호")
    parent_email: Optional[str] = Field(None, description="부모님 이메일 (선택)")
    interests: Optional[str] = Field(None, description="관심사 텍스트")
    view_time: Optional[int] = Field(None, description="관람 시간(분)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "홍길동",
                "parent_phone": "010-1234-5678",
                "parent_email": "parents@email.com",
                "interests": "도자기, 금속",
                "view_time": 60
            }
        }
    )

class LoginResponse(BaseModel):
    message: str
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)