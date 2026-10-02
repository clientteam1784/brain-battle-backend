from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        *,
        include_status: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.include_status = include_status


def _validation_message(error: dict) -> str:
    field = error.get("loc", [""])[-1]
    if error.get("type") == "greater_than_equal":
        if field == "questionNumber":
            return "문제 번호는 1 이상이어야 합니다."
        if field == "maxSubmitCount":
            return "최대 제출 횟수는 1 이상이어야 합니다."
    context = error.get("ctx") or {}
    nested_error = context.get("error")
    if nested_error:
        return str(nested_error)
    return error.get("msg", "잘못된 요청입니다.")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        content = {"message": exc.message}
        if exc.include_status:
            content = {"status": exc.status_code, **content}
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = _validation_message(exc.errors()[0])
        content = {"message": message}
        if request.url.path.startswith("/questions"):
            content = {"status": 400, **content}
        return JSONResponse(status_code=400, content=content)
