"""Pydantic schemas for Doctor Search, Filters, and Autocomplete."""

import uuid

from pydantic import BaseModel, Field

from app.models.doctor import VerificationStatus


class DoctorSearchFilterParams(BaseModel):
    q: str | None = Field(None, description="Search term for doctor name, hospital, or keywords")
    specialization_id: uuid.UUID | None = Field(None, description="Filter by specialization UUID")
    specialization_slug: str | None = Field(None, description="Filter by specialization slug")
    city_id: uuid.UUID | None = Field(None, description="Filter by city UUID")
    hospital_name: str | None = Field(None, description="Filter by hospital name")
    min_experience: int | None = Field(None, ge=0, le=70, description="Minimum years of clinical experience")
    max_experience: int | None = Field(None, ge=0, le=70, description="Maximum years of clinical experience")
    verified_only: bool = Field(False, description="Show only DoctorIn Verified practitioners")
    sort_by: str = Field(
        "relevance",
        pattern="^(relevance|experience_desc|verified_first|recently_added)$",
        description="Ranking order strategy",
    )
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=50)


class DoctorSearchResultItem(BaseModel):
    id: uuid.UUID
    full_name: str
    slug: str
    headline: str | None = None
    current_organization: str | None = None
    years_of_experience: int | None = None
    verification_status: VerificationStatus
    profile_photo_key: str | None = None
    profile_completion: int
    specializations: list[dict] = []


class SearchSuggestionItem(BaseModel):
    title: str
    type: str  # 'doctor', 'specialization', 'hospital'
    subtitle: str | None = None
    slug: str


class LookupItem(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
