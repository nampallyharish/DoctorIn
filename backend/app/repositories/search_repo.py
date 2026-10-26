"""Search Repository implementing multi-field filtering and transparent ranking."""

from sqlalchemy import and_, case, desc, func, nullslast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import City
from app.models.doctor import (
    Doctor,
    DoctorSpecialization,
    Specialization,
    VerificationStatus,
)
from app.schemas.search import DoctorSearchFilterParams


class SearchRepository:
    """Advanced search repository with filtering and defensible ranking."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_doctors(
        self,
        filters: DoctorSearchFilterParams,
    ) -> tuple[list[Doctor], int]:
        """
        Execute multi-factor doctor search with transparent ranking.
        Ranking formula:
        1. Exact/Prefix name and specialization matches
        2. Verified badge boost (verified doctors ranked higher in relevance)
        3. Profile completeness weighting
        4. Years of clinical experience
        """
        query = (
            select(Doctor)
            .options(
                selectinload(Doctor.specializations).selectinload(
                    DoctorSpecialization.specialization
                ),
            )
            .distinct()
        )

        conditions = []

        # 1. Text Query Filter (Full name, Headline, Bio, Organization)
        if filters.q and filters.q.strip():
            term = f"%{filters.q.strip()}%"
            # Join with specializations for matching specialization names
            text_cond = or_(
                Doctor.full_name.ilike(term),
                Doctor.headline.ilike(term),
                Doctor.bio.ilike(term),
                Doctor.current_organization.ilike(term),
                Doctor.id.in_(
                    select(DoctorSpecialization.doctor_id)
                    .join(Specialization)
                    .where(Specialization.name.ilike(term))
                ),
            )
            conditions.append(text_cond)

        # 2. Specialization Filters
        if filters.specialization_id:
            conditions.append(
                Doctor.id.in_(
                    select(DoctorSpecialization.doctor_id).where(
                        DoctorSpecialization.specialization_id == filters.specialization_id
                    )
                )
            )
        elif filters.specialization_slug:
            conditions.append(
                Doctor.id.in_(
                    select(DoctorSpecialization.doctor_id)
                    .join(Specialization)
                    .where(Specialization.slug == filters.specialization_slug)
                )
            )

        # 3. City Filter
        if filters.city_id:
            conditions.append(Doctor.current_city_id == filters.city_id)

        # 4. Hospital Filter
        if filters.hospital_name and filters.hospital_name.strip():
            conditions.append(
                Doctor.current_organization.ilike(f"%{filters.hospital_name.strip()}%")
            )

        # 5. Experience Range Filter
        if filters.min_experience is not None:
            conditions.append(Doctor.years_of_experience >= filters.min_experience)
        if filters.max_experience is not None:
            conditions.append(Doctor.years_of_experience <= filters.max_experience)

        # 6. Verified Only Filter
        if filters.verified_only:
            conditions.append(Doctor.verification_status == VerificationStatus.VERIFIED)

        # Apply all where conditions
        if conditions:
            query = query.where(and_(*conditions))

        # 7. Apply Transparent Ranking / Sorting
        if filters.sort_by == "experience_desc":
            query = query.order_by(
                nullslast(desc(Doctor.years_of_experience)),
                desc(Doctor.profile_completion),
            )
        elif filters.sort_by == "recently_added":
            query = query.order_by(desc(Doctor.created_at))
        elif filters.sort_by == "verified_first" or filters.sort_by == "relevance":
            # Transparent ranking: Verified first, then highest profile completion, then clinical experience
            verified_boost = case(
                (Doctor.verification_status == VerificationStatus.VERIFIED, 100),
                else_=0,
            )
            query = query.order_by(
                desc(verified_boost),
                desc(Doctor.profile_completion),
                nullslast(desc(Doctor.years_of_experience)),
                desc(Doctor.created_at),
            )

        # Count total matches
        count_query = select(func.count(func.distinct(Doctor.id)))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_count = await self.session.scalar(count_query) or 0

        # Pagination
        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)

        results = await self.session.execute(query)
        doctors = list(results.scalars().all())

        return doctors, total_count

    async def get_autocomplete_suggestions(self, term: str, limit: int = 8):
        """Fetch fast suggestions for search query autocomplete."""
        clean = f"%{term.strip()}%"
        suggestions = []

        # 1. Matching Doctors
        doc_q = (
            select(Doctor.full_name, Doctor.slug, Doctor.headline)
            .where(Doctor.full_name.ilike(clean))
            .limit(4)
        )
        doc_res = await self.session.execute(doc_q)
        for row in doc_res:
            suggestions.append(
                {
                    "title": row.full_name,
                    "type": "doctor",
                    "subtitle": row.headline or "Doctor",
                    "slug": f"/doctors/{row.slug}",
                }
            )

        # 2. Matching Specializations
        spec_q = (
            select(Specialization.name, Specialization.slug)
            .where(Specialization.name.ilike(clean), Specialization.is_active.is_(True))
            .limit(4)
        )
        spec_res = await self.session.execute(spec_q)
        for row in spec_res:
            suggestions.append(
                {
                    "title": row.name,
                    "type": "specialization",
                    "subtitle": "Medical Specialty",
                    "slug": f"/search?specialization_slug={row.slug}",
                }
            )

        return suggestions[:limit]

    async def get_all_specializations(self) -> list[Specialization]:
        """Fetch list of all active medical specializations."""
        query = (
            select(Specialization)
            .where(Specialization.is_active.is_(True))
            .order_by(Specialization.name.asc())
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_all_cities(self) -> list[City]:
        """Fetch list of all active cities."""
        query = (
            select(City)
            .where(City.is_active.is_(True))
            .order_by(City.name.asc())
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())
