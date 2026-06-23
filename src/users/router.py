from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database import get_db
from src.users import service as users_service
from src.users.schemas import LoginRequest, LoginResponse, InterestChoiceResponse
from src.users.constants import INTEREST_CHOICES

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/interests", response_model=List[InterestChoiceResponse])
async def get_interest_choices() -> List[InterestChoiceResponse]:
    # 관심사 카테고리 목록 조회 API
    return [
        InterestChoiceResponse(code=choice["code"], name=choice["name"]) 
        for choice in INTEREST_CHOICES
    ]

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    # 학생 로그인 및 자동 회원가입 API
    
    if login_data.interests:
        formatted_interests = ",".join(login_data.interests)
    else:
        formatted_interests = ""
        
    processed_data = login_data.model_copy(update={"interests": formatted_interests})
    user = await users_service.authenticate_or_register_user(db, processed_data)
    
    return LoginResponse(
        message="로그인이 성공적으로 완료되었습니다.",
        user_id=user.id,
        name=user.name,
    )