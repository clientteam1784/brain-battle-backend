from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _validation_message(error: dict) -> str:
    field = error.get("loc", [""])[-1]
    if error.get("type") == "greater_than_equal":
        if field == "questionNumber":
            return "문제 번호는 1 이상이어야 합니다."
        if field == "maxSubmitCount":
            return "최대 제출 횟수는 1회 이상이어야 합니다."
    context = error.get("ctx") or {}
    nested_error = context.get("error")
    if nested_error:
        return str(nested_error)
    return error.get("msg", "잘못된 요청입니다.")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"message": exc.message})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = _validation_message(exc.errors()[0])
        return JSONResponse(status_code=400, content={"message": message})
