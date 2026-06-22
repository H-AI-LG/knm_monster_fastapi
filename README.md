# KNM Monster FastAPI

**유물수호자 (Relic Guardians)** 백엔드 API 서버.  
국립중앙박물관 명품 30선 기반 교육 게임의 AI 대화 및 유물 데이터를 제공합니다.

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프레임워크 | FastAPI 0.115 + Python 3.12 |
| 구조 | [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) 도메인 기반 |
| 주요 기능 | AI 유물 정령 대화 생성, 칭찬 배틀 점수 분석 |
| 프론트엔드 | [knm_monsters](https://github.com/H-AI-LG/knm_monsters) |

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/api/chat` | 유물 정령 AI 대화 |
| POST | `/api/chat/praise` | 칭찬 배틀 텍스트 분석 |
| GET | `/api/artifacts` | 유물 목록 조회 |
| GET | `/api/artifacts/{id}` | 유물 상세 조회 |

### 프로젝트 구조

```
src/
├── main.py           # FastAPI 앱 진입점
├── config.py         # 환경변수 설정 (pydantic-settings)
├── models.py         # 전역 Pydantic 베이스 모델
├── exceptions.py     # 전역 예외 처리
├── ai/               # AI 대화 모듈
│   ├── router.py
│   ├── schemas.py
│   ├── service.py    # ← AI 제공자 연동 위치
│   ├── constants.py
│   └── exceptions.py
└── artifacts/        # 유물 데이터 모듈
    ├── router.py
    ├── schemas.py
    ├── service.py    # ← DB 연동 위치
    ├── constants.py
    └── exceptions.py
```

---

## 로컬 실행

### 1. 환경 설정

```bash
git clone https://github.com/H-AI-LG/knm_monster_fastapi.git
cd knm_monster_fastapi

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements/dev.txt
```

### 2. 환경변수

```bash
cp .env.example .env
# .env 파일을 열어 필요한 값 입력
```

### 3. 서버 실행

```bash
uvicorn src.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 테스트

```bash
pytest
```

### 5. 린트

```bash
ruff check .
ruff format .
```

---

## 팀 작업 분담

| 파트 | 파일 |
|------|------|
| AI 연동 | `src/ai/service.py` |
| DB / 유물 데이터 | `src/artifacts/service.py` |
