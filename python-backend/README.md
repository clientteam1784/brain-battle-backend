# Brain Battle Python backend

FastAPI, SQLAlchemy 2.x, Alembic으로 구현한 Brain Battle 백엔드입니다.

## Local setup

Python 3.12 이상과 `uv` 사용을 권장합니다.

```bash
uv sync --locked --extra dev
copy .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

- API 문서: <http://localhost:8000/docs>
- 상태 확인: <http://localhost:8000/health>
- 테스트: `uv run pytest`
- 프론트엔드 연동 가이드: `../docs/FRONTEND_API_GUIDE.md`
- 정적 OpenAPI 명세: `../docs/openapi.json`

API 계약을 변경한 뒤에는 다음 명령으로 정적 OpenAPI 명세를 갱신합니다.

```bash
uv run python scripts/export_openapi.py
```

실제 비밀번호는 `.env` 또는 배포 플랫폼의 secret에만 저장하고 Git에는 커밋하지 않습니다.

필수 운영 환경변수는 다음과 같습니다.

- `DATABASE_URL`: MySQL 연결 주소
- `JWT_SECRET`: JWT 서명용 32바이트 이상의 임의 문자열
- `TEACHER_ACCESS_CODE`: 교사 로그인 접근 코드
- `CORS_ORIGINS`: 허용할 프론트엔드 origin 목록

## Migration strategy

1. 새 테스트 DB에는 `alembic upgrade head`로 스키마를 생성합니다.
2. 기존 MySQL에는 바로 migration을 실행하지 않습니다. 먼저 데이터 백업과 중복 데이터 검사를 합니다.
3. 기존 Hibernate 테이블과 Alembic 메타데이터가 일치하면 `alembic stamp 20260911_01`로 기준점을 기록한 뒤 `alembic upgrade head`를 실행합니다.
4. 스테이징에서 로그인, 팀 PIN, 일괄 제출, 완료 처리, 순위 정렬을 확인합니다.

## Intentional hardening

- 문제 번호는 전체에서 유일합니다.
- 방 안의 모둠 이름, 모둠 안의 학번, 모둠-문제 답안은 각각 복합 유니크 제약을 가집니다.
- 답안 제출 시 팀과 기존 답안을 잠가 동시 제출로 인한 점수 중복 증가를 방지합니다.
- JWT의 교사/학생 역할과 팀 범위로 API 접근을 제한합니다.
- 문제별 최대 제출 횟수, 미제출/오답 구분, 10문항 일괄 채점과 재도전 로테이션을 제공합니다.
- 학생 등록 응답은 ORM 객체 전체가 아니라 `id`, `studentNumber`, `teamId`만 반환합니다.

운영 DB에 유니크 제약을 추가하기 전에는 기존 중복 데이터를 반드시 확인해야 합니다.
