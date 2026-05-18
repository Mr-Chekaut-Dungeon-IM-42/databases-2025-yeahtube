from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.domain.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    GoneError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # The domain message is already expressed in business language.
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def not_found_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def unauthorized_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def forbidden_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def gone_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    # Order matters: the more specific handler should be registered explicitly.
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(GoneError, gone_error_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ConflictError, domain_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
