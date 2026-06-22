from fastapi import APIRouter

from src.ai.schemas import ChatRequest, ChatResponse, PraiseRequest, PraiseResponse
from src.ai import service as ai_service

router = APIRouter(prefix="/chat", tags=["ai"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await ai_service.chat(request)


@router.post("/praise", response_model=PraiseResponse)
async def analyze_praise(request: PraiseRequest) -> PraiseResponse:
    return await ai_service.analyze_praise(request)
