"""Search and Discovery REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import APIResponse, MetaData
from app.schemas.search import (
    DoctorSearchFilterParams,
    DoctorSearchResultItem,
    LookupItem,
    SearchSuggestionItem,
)
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search & Discovery"])


@router.get(
    "/doctors",
    response_model=APIResponse[list[DoctorSearchResultItem]],
    summary="Multi-factor Doctor Search with Filters and Defensible Ranking",
)
async def search_doctors(
    q: str | None = Query(None, description="Search query"),
    specialization_id: uuid.UUID | None = Query(None),
    specialization_slug: str | None = Query(None),
    city_id: uuid.UUID | None = Query(None),
    hospital_name: str | None = Query(None),
    min_experience: int | None = Query(None, ge=0),
    max_experience: int | None = Query(None, ge=0),
    verified_only: bool = Query(False),
    sort_by: str = Query("relevance", pattern="^(relevance|experience_desc|verified_first|recently_added)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Search doctors with filters across specialization, city, experience, verification status, and hospital.
    """
    filters = DoctorSearchFilterParams(
        q=q,
        specialization_id=specialization_id,
        specialization_slug=specialization_slug,
        city_id=city_id,
        hospital_name=hospital_name,
        min_experience=min_experience,
        max_experience=max_experience,
        verified_only=verified_only,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )

    service = SearchService(db)
    items, total_count = await service.search_doctors(filters)

    return APIResponse(
        success=True,
        data=items,
        meta=MetaData(page=page, per_page=per_page, total=total_count),
    )


@router.get(
    "/suggest",
    response_model=APIResponse[list[SearchSuggestionItem]],
    summary="Instant Autocomplete for Search Bar",
)
async def get_autocomplete_suggestions(
    q: str = Query(..., min_length=2, description="Search prefix"),
    db: AsyncSession = Depends(get_db),
):
    """Returns fast suggestions across doctors, specialties, and hospitals."""
    service = SearchService(db)
    suggestions = await service.get_suggestions(q)
    return APIResponse(success=True, data=suggestions)


@router.get(
    "/specializations",
    response_model=APIResponse[list[LookupItem]],
    summary="List all Medical Specializations",
)
async def get_specializations(
    db: AsyncSession = Depends(get_db),
):
    """List active medical specialties for dropdowns and filter sidebars."""
    service = SearchService(db)
    specialties = await service.get_specializations()
    return APIResponse(success=True, data=specialties)


@router.get(
    "/cities",
    response_model=APIResponse[list[LookupItem]],
    summary="List all Cities",
)
async def get_cities(
    db: AsyncSession = Depends(get_db),
):
    """List active cities for search location filtering."""
    service = SearchService(db)
    cities = await service.get_cities()
    return APIResponse(success=True, data=cities)
