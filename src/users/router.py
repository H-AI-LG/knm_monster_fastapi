from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users import service as users_service
from src.users.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    ### 🔑 학생 로그인 및 자동 회원가입 API
    """
    user = await users_service.authenticate_or_register_user(db, login_data)
    return LoginResponse(
        message="로그인이 성공적으로 완료되었습니다.",
        user_id=user.id,
        name=user.name,
    )