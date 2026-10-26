"""Common schemas for standard API response envelopes, errors, and pagination."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str
    field: str | None = None
    details: dict | None = None


class MetaData(BaseModel):
    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    total_pages: int | None = None
    cursor: str | None = None
    has_next: bool | None = None


class APIResponse(BaseModel, Generic[T]):
    """Standard unified response envelope for all API endpoints."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    data: T | None = None
    meta: MetaData | None = None
    errors: list[APIError] | None = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class CursorPaginationParams(BaseModel):
    cursor: str | None = Field(default=None, description="Cursor for pagination")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum items to return")
