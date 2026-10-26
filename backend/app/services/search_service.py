"""Search Service coordinating doctor search, autocomplete, and lookup lists."""


from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.search_repo import SearchRepository
from app.schemas.search import (
    DoctorSearchFilterParams,
    DoctorSearchResultItem,
    LookupItem,
    SearchSuggestionItem,
)


class SearchService:
    """Coordinates multi-factor search, ranking, and autocomplete."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SearchRepository(db)

    async def search_doctors(
        self,
        filters: DoctorSearchFilterParams,
    ) -> tuple[list[DoctorSearchResultItem], int]:
        """Execute doctor search and map results into response schemas."""
        doctors, total_count = await self.repo.search_doctors(filters)

        items = []
        for d in doctors:
            specs = []
            if d.specializations:
                for ds in d.specializations:
                    if ds.specialization:
                        specs.append(
                            {
                                "id": str(ds.specialization.id),
                                "name": ds.specialization.name,
                                "slug": ds.specialization.slug,
                                "is_primary": ds.is_primary,
                            }
                        )

            items.append(
                DoctorSearchResultItem(
                    id=d.id,
                    full_name=d.full_name,
                    slug=d.slug,
                    headline=d.headline,
                    current_organization=d.current_organization,
                    years_of_experience=d.years_of_experience,
                    verification_status=d.verification_status,
                    profile_photo_key=d.profile_photo_key,
                    profile_completion=d.profile_completion,
                    specializations=specs,
                )
            )

        return items, total_count

    async def get_suggestions(self, term: str) -> list[SearchSuggestionItem]:
        """Fetch fast autocomplete suggestions."""
        if not term or len(term.strip()) < 2:
            return []
        raw_items = await self.repo.get_autocomplete_suggestions(term.strip())
        return [SearchSuggestionItem(**item) for item in raw_items]

    async def get_specializations(self) -> list[LookupItem]:
        """Fetch all medical specializations."""
        specs = await self.repo.get_all_specializations()
        return [
            LookupItem(id=s.id, name=s.name, slug=s.slug, description=s.description)
            for s in specs
        ]

    async def get_cities(self) -> list[LookupItem]:
        """Fetch all cities."""
        cities = await self.repo.get_all_cities()
        return [
            LookupItem(id=c.id, name=c.name, slug=c.slug, description=c.state)
            for c in cities
        ]
