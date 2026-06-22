# CLAUDE.md

FastAPI 백엔드 서버. 유물수호자 게임의 AI 대화 생성 및 유물 데이터를 제공합니다.

## 프로젝트 구조

```
src/
├── main.py           # FastAPI 앱 + CORS + 라우터 등록
├── config.py         # pydantic-settings 환경변수
├── models.py         # CustomModel 전역 베이스
├── exceptions.py     # AppException 전역 베이스 + 핸들러
├── ai/               # AI 대화 모듈
│   ├── router.py     # POST /api/chat, POST /api/chat/praise
│   ├── schemas.py    # ChatRequest/Response, PraiseRequest/Response
│   ├── service.py    # ← AI 연동 TODO
│   └── constants.py  # 대화 단계 상수 (greeting/dialogue/quiz/praise)
└── artifacts/        # 유물 데이터 모듈
    ├── router.py     # GET /api/artifacts, GET /api/artifacts/{id}
    ├── schemas.py    # ArtifactResponse, ArtifactQuiz
    └── service.py    # ← DB 연동 TODO
```

## 핵심 패턴

### 새 모듈 추가 시
`src/<module>/` 디렉토리를 만들고 아래 파일을 생성하세요:
- `router.py` — APIRouter 정의
- `schemas.py` — Pydantic 입출력 모델 (CustomModel 상속)
- `service.py` — 비즈니스 로직
- `exceptions.py` — `AppException` 상속한 모듈 전용 예외
- `constants.py` — 상수
- `src/main.py`에 `app.include_router(...)` 추가

### 예외 처리
항상 `src.exceptions.AppException`을 상속해서 만드세요:
```python
from src.exceptions import AppException

class ArtifactNotFound(AppException):
    def __init__(self, artifact_id: str):
        super().__init__(status_code=404, detail=f"유물을 찾을 수 없습니다: {artifact_id}")
```

### 스키마
`src.models.CustomModel`을 상속하세요 (`BaseModel` 직접 사용 금지):
```python
from src.models import CustomModel

class MyResponse(CustomModel):
    id: str
    name: str
```

## TODO 위치

| 파일 | 작업 내용 |
|------|----------|
| `src/ai/service.py` | AI 제공자 연동 (chat, analyze_praise) |
| `src/artifacts/service.py` | DB 연동 (list, get) |

## 로컬 실행

```bash
source .venv/bin/activate
uvicorn src.main:app --reload
# Swagger: http://localhost:8000/docs
```

## 테스트 / 린트

```bash
pytest                  # 전체 테스트
ruff check . --fix      # 린트 자동 수정
ruff format .           # 포맷팅
```

## 관련 레포

- 프론트엔드: [knm_monsters](https://github.com/H-AI-LG/knm_monsters)
- 배포: CloudFront `https://knm.ai.kr` + S3 버킷 `knm-monsters-game-1782044138`
