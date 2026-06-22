---
paths:
  - "**/*.py"
---

# Python 코딩 규칙

## 공통

- Python 3.12+ 문법 사용 (`X | Y` 유니온, `match` 등)
- 타입 힌트 필수. `Any` 사용 최소화
- 비동기 I/O는 `async/await` 사용. 동기 블로킹 함수를 `async def` 안에서 직접 호출 금지

## FastAPI

- 라우터 함수는 반드시 `response_model` 지정
- 서비스 로직은 `service.py`에만. 라우터에 비즈니스 로직 작성 금지
- 예외는 `AppException` 상속 후 raise. `HTTPException` 직접 사용 금지

## Pydantic

- 모든 스키마는 `CustomModel` 상속 (`src.models` 임포트)
- `BaseModel` 직접 상속 금지

## 임포트 순서 (ruff I 규칙 준수)

1. 표준 라이브러리
2. 서드파티 (`fastapi`, `pydantic` 등)
3. 내부 모듈 (`src.*`)
