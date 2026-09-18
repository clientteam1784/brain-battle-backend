from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_settings
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Production schema changes are managed exclusively by Alembic.
    yield


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
