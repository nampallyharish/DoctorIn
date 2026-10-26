"""Custom domain exceptions and FastAPI exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import logger


class DoctorInException(Exception):
    """Base exception for all domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(DoctorInException):
    def __init__(self, resource: str, identifier: Any = None):
        msg = f"{resource} not found" if not identifier else f"{resource} '{identifier}' not found"
        super().__init__(
            message=msg,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


class UnauthorizedError(DoctorInException):
    def __init__(self, message: str = "Authentication required", code: str = "UNAUTHORIZED"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(DoctorInException):
    def __init__(self, message: str = "Access denied", code: str = "FORBIDDEN"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(DoctorInException):
    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors or []},
        )


class ConflictError(DoctorInException):
    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitExceededError(DoctorInException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )


class InvalidOTPError(DoctorInException):
    def __init__(
        self,
        message: str = "Invalid verification code",
        code: str = "INVALID_OTP",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        attempts_left: int | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details={"attempts_left": attempts_left} if attempts_left is not None else {},
        )


class OTPExpiredError(DoctorInException):
    def __init__(self, message: str = "This OTP has expired. Please request a new code."):
        super().__init__(
            message=message,
            code="OTP_EXPIRED",
            status_code=status.HTTP_410_GONE,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application."""

    @app.exception_handler(DoctorInException)
    async def handle_doctorin_exception(request: Request, exc: DoctorInException) -> JSONResponse:
        logger.warning(
            f"Domain exception: {exc.code} - {exc.message}",
            extra={"extra_data": {"path": request.url.path, "code": exc.code, "details": exc.details}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "errors": [
                    {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details,
                    }
                ],
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for err in exc.errors():
            loc = ".".join(str(l) for l in err.get("loc", []))
            errors.append(
                {
                    "code": "VALIDATION_ERROR",
                    "field": loc,
                    "message": err.get("msg", "Invalid value"),
                }
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "data": None,
                "errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled server error on {request.url.path}: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "errors": [
                    {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred. Please try again later.",
                    }
                ],
            },
        )
