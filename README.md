# Brain Battle Backend

Brain Battle의 FastAPI 백엔드입니다.

## Project structure

- `python-backend/`: FastAPI, SQLAlchemy, Alembic 애플리케이션
- `docs/FRONTEND_API_GUIDE.md`: 프론트엔드 연동 가이드
- `docs/openapi.json`: 정적 OpenAPI 계약

## Quick start

Python 3.12 이상과 `uv`가 필요합니다.

```bash
cd python-backend
uv sync --locked --extra dev
copy .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- 테스트: `uv run pytest`

운영 DB에 마이그레이션을 적용하기 전에 데이터를 백업하고 기존 중복 데이터를 확인해야 합니다. 실제 접속 정보는 `.env` 또는 배포 환경의 secret에만 저장합니다.

