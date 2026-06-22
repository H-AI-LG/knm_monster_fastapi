from src.ai.schemas import ChatRequest, ChatResponse, PraiseRequest, PraiseResponse
from src.ai.exceptions import AIServiceError


async def chat(request: ChatRequest) -> ChatResponse:
    # TODO: AI 제공자 연동 (Gemini / Claude / OpenAI)
    # - greeting/dialogue: 유물 정령 페르소나로 대화 생성
    # - quiz: 퀴즈 결과 피드백
    # - praise: 칭찬 배틀 점수 분석 → PraiseRequest 사용 권장
    raise AIServiceError("AI 서비스가 아직 구현되지 않았습니다")


async def analyze_praise(request: PraiseRequest) -> PraiseResponse:
    # TODO: 유저가 입력한 칭찬 텍스트를 AI로 분석
    # - 역사 팩트 일치도 + 감성 점수 → 0.0~1.0 반환
    # - 이 점수가 보스 대미지 배율로 사용됨
    raise AIServiceError("칭찬 배틀 분석이 아직 구현되지 않았습니다")
