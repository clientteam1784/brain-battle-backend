# Brain Battle Backend

Brain Battle의 FastAPI, SQLAlchemy 2.x, Alembic 백엔드입니다.
기존 `clientteam1784/brain-battle`에서 백엔드 코드와 커밋 기록을 이전했습니다.
프론트엔드는 별도 저장소 [brain-battle-frontend](https://github.com/clientteam1784/brain-battle-frontend)에서 개발합니다.

## API documentation

- **[전체 API 명세서](docs/API_SPEC.md)**: 구현된 19개 API의 권한, request/response, 오류 응답
- [프론트엔드 연동 가이드](docs/FRONTEND_API_GUIDE.md): 모둠 PIN 입장, 일괄 제출, 로테이션 화면 흐름
- [OpenAPI JSON](docs/openapi.json): 필드 자료형·필수 여부와 기계 판독 계약

모둠 생성은 선생님이 하고 학생은 모둠 PIN으로 로그인합니다. 새로운 답안 화면은
10문항을 입력한 뒤 단일 제출 버튼에서 일괄 채점 API를 사용합니다.

## Project structure

- `app/`: API, 인증, 데이터 모델, 채점 로직
- `migrations/`: Alembic DB 마이그레이션
- `tests/`: API 및 게임 흐름 테스트
- `scripts/`: OpenAPI 명세 생성
- `.github/workflows/`: 자동 검사 설정
- `docs/API_SPEC.md`: 전체 백엔드 API 명세
- `docs/FRONTEND_API_GUIDE.md`: 프론트엔드 연동 가이드
- `docs/openapi.json`: 정적 OpenAPI 계약

## Quick start

Python 3.12 이상과 `uv`가 필요합니다.

```bash
uv sync --locked --extra dev
copy .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- 테스트: `uv run pytest`

API 변경 후에는 `uv run python scripts/export_openapi.py`로 정적 명세를 갱신합니다.
Docker 빌드는 저장소 최상위에서 `docker build -t brain-battle-backend .`로 실행합니다.

## Environment

- `DATABASE_URL`: MySQL 연결 주소
- `JWT_SECRET`: JWT 서명용 32바이트 이상의 임의 문자열
- `TEACHER_ACCESS_CODE`: 교사 로그인 접근 코드
- `CORS_ORIGINS`: 허용할 프론트엔드 origin 목록

## Features

- JWT 교사·학생 역할 인증 및 모둠 범위별 접근 제한
- 선생님의 모둠 생성 및 학생의 모둠 PIN 로그인
- 문제별 최대 제출 횟수와 미제출·오답 상태 구분
- 10문항 일괄 채점과 미제출·오답 문항 로테이션
- 모둠 현황, 정답 수, 남은 문제 수, 제출·수정 횟수 및 순위 조회
- 제출 시 모둠과 답안 잠금 및 유니크 제약으로 중복 점수 증가 방지

## Database migration

새 DB는 `uv run alembic upgrade head`로 생성합니다. 기존 Hibernate 테이블이 초기
Alembic 스키마와 일치할 때만 `uv run alembic stamp 20260911_01`로 기준점을 기록한 뒤
`uv run alembic upgrade head`를 실행합니다. 스테이징에서 로그인, 모둠 PIN, 일괄 제출,
완료 처리 및 순위를 확인합니다.

운영 DB에 마이그레이션을 적용하기 전에 데이터를 백업하고 기존 중복 데이터를 확인해야 합니다. 실제 접속 정보는 `.env` 또는 배포 환경의 secret에만 저장합니다.

