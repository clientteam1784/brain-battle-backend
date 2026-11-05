from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_settings
from app.exceptions import register_exception_handlers


# 앱 시작/종료 시 실행할 작업을 모읍니다. DB 스키마 변경은 Alembic이 담당합니다.
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Production schema changes are managed exclusively by Alembic.
    yield


# FastAPI 앱, CORS 정책, 예외 처리기, API 라우터를 조립합니다.
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Brain Battle API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
