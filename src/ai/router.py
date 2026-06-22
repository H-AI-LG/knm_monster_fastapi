from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai import service as ai_service
from src.ai.schemas import ChatRequest, ChatResponse, PraiseRequest, PraiseResponse
from src.database import get_db

router = APIRouter(prefix="/chat", tags=["ai"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    return await ai_service.chat(request, db)


@router.post("/praise", response_model=PraiseResponse)
async def analyze_praise(
    request: PraiseRequest,
    db: AsyncSession = Depends(get_db),
) -> PraiseResponse:
    return await ai_service.analyze_praise(request, db)
