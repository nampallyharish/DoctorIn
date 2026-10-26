"""HTTP request and response logging middleware."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests with latency and status code."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        process_time_ms = round((time.time() - start_time) * 1000, 2)
        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} ({process_time_ms}ms)",
            extra={
                "extra_data": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": process_time_ms,
                    "client_ip": client_ip,
                }
            },
        )
        return response
