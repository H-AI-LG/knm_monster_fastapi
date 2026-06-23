# KNM Monster FastAPI

**유물수호자 (Relic Guardians)** 백엔드 API 서버.  
국립중앙박물관 명품 30선 기반 교육 게임의 AI 대화 및 유물 데이터를 제공합니다.

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프레임워크 | FastAPI 0.115 + Python 3.12 |
| AI | AWS Bedrock — Claude Haiku 4.5 (ap-northeast-2) |
| DB | PostgreSQL 16 (로컬: Docker / 배포: RDS) |
| 구조 | [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) 도메인 기반 |
| 프론트엔드 | [knm_monsters](https://github.com/H-AI-LG/knm_monsters) |

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/api/chat` | 유물 정령 AI 대화 |
| POST | `/api/chat/praise` | 칭찬 배틀 텍스트 분석 |
| GET | `/api/artifacts` | 유물 목록 조회 (`?zone=` 필터 가능) |
| GET | `/api/artifacts/recommend/{user_id}` | 관심사 기반 유물 추천 |
| GET | `/api/artifacts/{id}` | 유물 상세 조회 |
| GET | `/api/artifacts/{id}/quizzes` | 유물 퀴즈 조회 |
| GET | `/api/users/interests` | 관심사 카테고리 목록 |
| POST | `/api/users/login` | 로그인 |
| POST | `/api/users/{user_id}/artifacts` | 유물 수집 기록 (퀴즈 통과 후 호출) |
| GET | `/api/users/{user_id}/artifacts` | 도감 조회 — 수집한 유물 목록 |

### 프로젝트 구조

```
src/
├── main.py           # FastAPI 앱 진입점
├── config.py         # 환경변수 설정 (pydantic-settings)
├── database.py       # SQLAlchemy 비동기 엔진
├── models.py         # 전역 Pydantic 베이스 모델
├── exceptions.py     # 전역 예외 처리
├── ai/               # AI 대화 모듈 (AWS Bedrock)
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── config.py
│   └── exceptions.py
├── artifacts/        # 유물 데이터 모듈
│   ├── router.py
│   ├── schemas.py
│   ├── models.py     # GameArtifact, UserArtifact(도감)
│   ├── service.py
│   └── exceptions.py
└── users/            # 유저 모듈
    ├── router.py
    ├── schemas.py
    ├── models.py
    ├── service.py
    ├── exceptions.py
    └── constants.py  # 관심사 카테고리
```

---

## 로컬 실행

### 사전 준비

- Python 3.12+
- Docker Desktop ([설치](https://www.docker.com/products/docker-desktop/))
- AWS 자격증명 (Bedrock 접근용)

---

### 1. 레포 클론

```bash
git clone https://github.com/H-AI-LG/knm_monster_fastapi.git
cd knm_monster_fastapi
```

### 2. 가상환경 생성 및 패키지 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### 3. PostgreSQL 실행 (Docker)

```bash
docker compose up -d
```

> `docker compose` 명령이 없으면 Docker Desktop이 설치되지 않은 것입니다.  
> [Docker Desktop 다운로드](https://www.docker.com/products/docker-desktop/)

### 4. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채워주세요:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/knm
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AI_MODEL=ap.anthropic.claude-haiku-4-5-20251001-v1:0
```

### 5. 유물 데이터 임포트 (최초 1회만)

국립중앙박물관 CSV 파일을 DB에 넣는 작업입니다. **한 번만 실행하면 됩니다.**

```bash
python scripts/seed.py --csv "/path/to/국립중앙박물관_e뮤지엄 유물정보.csv"
```

약 1~2분 소요, 100,000행 임포트됩니다.

유물 데이터를 DB에 넣는 작업입니다. **한 번만 실행하면 됩니다.**
```bash
python scripts/seed_game.py
```

> Docker 볼륨이 유지되는 한 재실행 불필요.  
> `docker compose down -v` 로 볼륨 삭제 시에는 재실행 필요.

### 6. 서버 실행

```bash
uvicorn src.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 이후 매번 실행 순서

```bash
docker compose up -d          # DB 켜기
source .venv/bin/activate     # 가상환경 활성화
uvicorn src.main:app --reload # 서버 실행
```

---

## API 테스트

Swagger UI(`/docs`)에서 `POST /api/chat` 호출:

```json
{
  "artifact_id": "artifact_001",
  "artifact_name": "주먹도끼",
  "message": "안녕! 나 박물관 처음 왔어",
  "stage": "greeting"
}
```

---

## 테스트 / 린트

```bash
pytest             # 전체 테스트
ruff check . --fix # 린트 자동 수정
ruff format .      # 포맷팅
```

---

## 팀 작업 분담

| 파트 | 파일 |
|------|------|
| AI 연동 | `src/ai/service.py` |
| DB / 유물 데이터 | `src/artifacts/service.py` |
