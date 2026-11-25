from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    DomainError,
    NotFoundError,
)

STATUS_CODES: dict[type[DomainError], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    BusinessRuleError: 400,
}


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    status_code = next(
        (code for error_type, code in STATUS_CODES.items() if isinstance(exc, error_type)),
        400,
    )
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
