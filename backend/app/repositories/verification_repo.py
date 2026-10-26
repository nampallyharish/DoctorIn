"""Doctor Verification Repository for requests, document uploads, and admin queues."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.doctor import (
    CredentialType,
    Doctor,
    DoctorCredential,
    VerificationStatus,
)
from app.models.verification import (
    VerificationDocument,
    VerificationRequest,
    VerificationRequestStatus,
)
from app.repositories.base import BaseRepository


class VerificationRepository(BaseRepository[VerificationRequest]):
    """Handles verification requests, credential submission, and admin queues."""

    def __init__(self, session: AsyncSession):
        super().__init__(VerificationRequest, session)

    async def get_latest_request_for_doctor(
        self, doctor_id: uuid.UUID
    ) -> VerificationRequest | None:
        """Fetch latest verification request with uploaded documents."""
        query = (
            select(VerificationRequest)
            .where(VerificationRequest.doctor_id == doctor_id)
            .options(
                selectinload(VerificationRequest.documents),
                selectinload(VerificationRequest.doctor),
            )
            .order_by(VerificationRequest.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_request_with_details(
        self, request_id: uuid.UUID
    ) -> VerificationRequest | None:
        """Fetch verification request by ID with all documents and doctor details."""
        query = (
            select(VerificationRequest)
            .where(VerificationRequest.id == request_id)
            .options(
                selectinload(VerificationRequest.documents),
                selectinload(VerificationRequest.doctor).selectinload(Doctor.user),
                selectinload(VerificationRequest.doctor).selectinload(Doctor.credentials),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_verification_request(
        self,
        doctor_id: uuid.UUID,
        credential_type: CredentialType,
        credential_number: str,
        issuing_authority: str,
        issuing_country: str = "IND",
        issue_date: date | None = None,
        expiry_date: date | None = None,
        document_key: str | None = None,
        document_original_name: str | None = None,
        document_mime_type: str | None = None,
        document_size_bytes: int | None = None,
        supporting_notes: str | None = None,
    ) -> VerificationRequest:
        """Create new verification request and add/update doctor credential."""
        now = datetime.now(timezone.utc)

        # 1. Create request record
        req = VerificationRequest(
            doctor_id=doctor_id,
            status=VerificationRequestStatus.PENDING,
            admin_notes=supporting_notes,
            submitted_at=now,
        )
        self.session.add(req)
        await self.session.flush()

        # 2. Add document if provided
        if document_key:
            doc = VerificationDocument(
                verification_request_id=req.id,
                document_type=credential_type.value,
                document_key=document_key,
                original_name=document_original_name or "credential_document",
                mime_type=document_mime_type or "application/pdf",
                size_bytes=document_size_bytes or 0,
            )
            self.session.add(doc)

        # 3. Add credential entry
        cred = DoctorCredential(
            doctor_id=doctor_id,
            credential_type=credential_type,
            credential_number=credential_number,
            issuing_authority=issuing_authority,
            issuing_country=issuing_country,
            issue_date=issue_date,
            expiry_date=expiry_date,
            document_key=document_key,
            document_original_name=document_original_name,
            document_mime_type=document_mime_type,
            document_size_bytes=document_size_bytes,
            verification_status="pending",
            submitted_at=now,
        )
        self.session.add(cred)

        # 4. Update Doctor verification_status to PENDING
        doctor_stmt = (
            update(Doctor)
            .where(Doctor.id == doctor_id)
            .values(verification_status=VerificationStatus.PENDING)
        )
        await self.session.execute(doctor_stmt)
        await self.session.flush()

        return req

    async def list_admin_queue(
        self,
        status_filter: VerificationRequestStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[VerificationRequest], int]:
        """List verification requests for admin review queue with count."""
        query = (
            select(VerificationRequest)
            .options(
                selectinload(VerificationRequest.doctor).selectinload(Doctor.user),
                selectinload(VerificationRequest.doctor).selectinload(Doctor.credentials),
                selectinload(VerificationRequest.documents),
            )
            .order_by(VerificationRequest.submitted_at.asc())
            .offset(skip)
            .limit(limit)
        )
        if status_filter:
            query = query.where(VerificationRequest.status == status_filter)

        count_query = select(func.count(VerificationRequest.id))
        if status_filter:
            count_query = count_query.where(VerificationRequest.status == status_filter)

        results = await self.session.execute(query)
        total = await self.session.scalar(count_query) or 0

        return list(results.scalars().all()), total
