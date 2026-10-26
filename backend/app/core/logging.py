"""Structured JSON logging configuration."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include exception tracebacks if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include custom extra attributes
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)

        # Ensure we never log sensitive fields
        sanitized = self._sanitize(log_data)
        return json.dumps(sanitized)

    @staticmethod
    def _sanitize(data: dict[str, Any]) -> dict[str, Any]:
        sensitive_keys = {
            "password",
            "password_hash",
            "otp",
            "otp_hash",
            "jwt_secret",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "authorization",
        }
        sanitized = {}
        for k, v in data.items():
            if k.lower() in sensitive_keys:
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = JSONFormatter._sanitize(v)
            else:
                sanitized[k] = v
        return sanitized


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure root logger with structured JSON formatting."""
    log_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger("doctorin")
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )

    return logger


logger = setup_logging()
