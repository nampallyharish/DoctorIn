"""Doctor Verification Business Logic Service."""

import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logging import logger
from app.models.doctor import (
    CredentialType,
    Doctor,
    DoctorCredential,
    Gender,
    VerificationStatus,
)
from app.models.user import User, UserRole
from app.models.verification import (
    VerificationDocument,
    VerificationRequest,
    VerificationRequestStatus,
)
from app.repositories.audit_repo import AuditRepository
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.verification_repo import VerificationRepository
from app.schemas.verification import (
    AdminVerificationQueueItem,
    AdminVerificationReviewRequest,
    DoctorApplicationRequest,
    VerificationDocumentItem,
    VerificationStatusResponse,
    VerificationSubmitRequest,
)
from app.services.file_service import FileService


class VerificationService:
    """Handles doctor verification lifecycle, document inspection, and admin reviews."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.doc_repo = DoctorRepository(db)
        self.ver_repo = VerificationRepository(db)
        self.audit_repo = AuditRepository(db)

    async def upload_verification_document(
        self,
        user: User,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> tuple[str, str]:
        """Upload verification document securely to private storage."""
        doctor = await self.doc_repo.get_by_user_id(user.id)
        entity_id = doctor.id if doctor else user.id

        storage_key, original_name = FileService.upload_document(
            file_obj=file_obj,
            entity_id=entity_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )

        return storage_key, original_name

    async def apply_doctor_account(
        self,
        user: User,
        payload: DoctorApplicationRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> VerificationRequest:
        """Create or update doctor profile and submit application for admin review."""
        now = datetime.now(timezone.utc)
        doctor = await self.doc_repo.get_by_user_id(user.id)

        if not doctor:
            name = payload.full_name.strip()
            base_slug = name.lower().replace(" ", "-").replace(".", "")
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            gender_val = None
            if payload.gender:
                try:
                    gender_val = Gender(payload.gender.lower())
                except ValueError:
                    gender_val = None

            doctor = Doctor(
                user_id=user.id,
                full_name=name,
                slug=slug,
                date_of_birth=payload.date_of_birth,
                gender=gender_val,
                profile_photo_key=payload.profile_photo_key,
                bio=payload.bio,
                headline=payload.designation,
                years_of_experience=payload.years_of_experience,
                current_organization=payload.current_hospital,
                verification_status=VerificationStatus.PENDING,
            )
            self.db.add(doctor)
            await self.db.flush()
        else:
            doctor.full_name = payload.full_name.strip()
            if payload.date_of_birth:
                doctor.date_of_birth = payload.date_of_birth
            if payload.gender:
                try:
                    doctor.gender = Gender(payload.gender.lower())
                except ValueError:
                    pass
            if payload.profile_photo_key:
                doctor.profile_photo_key = payload.profile_photo_key
            if payload.bio:
                doctor.bio = payload.bio
            if payload.designation:
                doctor.headline = payload.designation
            doctor.years_of_experience = payload.years_of_experience
            if payload.current_hospital:
                doctor.current_organization = payload.current_hospital
            doctor.verification_status = VerificationStatus.PENDING

        # Add education entries
        for edu in payload.education:
            await self.doc_repo.add_education(
                doctor_id=doctor.id,
                degree=edu.degree,
                institution=edu.institution,
                start_year=edu.graduation_year,
                field_of_study=edu.field_of_study,
            )

        # Create VerificationRequest
        req = VerificationRequest(
            doctor_id=doctor.id,
            status=VerificationRequestStatus.PENDING,
            submitted_at=now,
        )
        self.db.add(req)
        await self.db.flush()

        # Add uploaded documents
        for doc in payload.documents:
            v_doc = VerificationDocument(
                verification_request_id=req.id,
                document_type=doc.document_type,
                document_key=doc.document_key,
                original_name=doc.original_name,
                mime_type=doc.mime_type,
                size_bytes=doc.size_bytes,
            )
            self.db.add(v_doc)

        # Add doctor credential
        cred = DoctorCredential(
            doctor_id=doctor.id,
            credential_type=CredentialType.MEDICAL_LICENSE,
            credential_number=payload.registration_number,
            issuing_authority=payload.council_name,
            issuing_country=payload.registration_country,
            issue_date=payload.registration_date,
            verification_status="pending",
            submitted_at=now,
        )
        if payload.documents:
            cred.document_key = payload.documents[0].document_key
            cred.document_original_name = payload.documents[0].original_name
            cred.document_mime_type = payload.documents[0].mime_type
            cred.document_size_bytes = payload.documents[0].size_bytes
        self.db.add(cred)

        await self.db.flush()

        # Audit log
        await self.audit_repo.log_action(
            action="DOCTOR_APPLICATION_SUBMITTED",
            resource_type="verification_request",
            actor_id=user.id,
            resource_id=req.id,
            details={
                "doctor_id": str(doctor.id),
                "council_name": payload.council_name,
                "registration_number": payload.registration_number,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(f"Doctor application submitted for user {user.id}, doctor {doctor.id}")
        return req

    async def submit_verification_request(
        self,
        user: User,
        payload: VerificationSubmitRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> VerificationRequest:
        """Submit medical credentials and document for admin review."""
        doctor = await self.doc_repo.get_by_user_id(user.id)
        if not doctor:
            # Create a placeholder doctor profile if one doesn't exist
            base_slug = f"dr-user-{str(uuid.uuid4())[:8]}"
            doctor = Doctor(
                user_id=user.id,
                full_name=user.email.split("@")[0] if user.email else "Dr. Applicant",
                slug=base_slug,
                verification_status=VerificationStatus.PENDING,
            )
            self.db.add(doctor)
            await self.db.flush()

        # If already verified, reject redundant submissions
        if doctor.verification_status == VerificationStatus.VERIFIED:
            raise ValidationError("Your account is already verified with an active DoctorIn badge.")

        # Create verification request and associate credentials
        req = await self.ver_repo.create_verification_request(
            doctor_id=doctor.id,
            credential_type=payload.credential_type,
            credential_number=payload.credential_number,
            issuing_authority=payload.issuing_authority,
            issuing_country=payload.issuing_country,
            issue_date=payload.issue_date,
            expiry_date=payload.expiry_date,
            document_key=payload.document_key,
            document_original_name=payload.document_original_name,
            document_mime_type=payload.document_mime_type,
            document_size_bytes=payload.document_size_bytes,
            supporting_notes=payload.supporting_notes,
        )

        # Record audit log
        await self.audit_repo.log_action(
            action="VERIFICATION_SUBMITTED",
            resource_type="verification_request",
            actor_id=user.id,
            resource_id=req.id,
            details={
                "doctor_id": str(doctor.id),
                "credential_number": payload.credential_number,
                "issuing_authority": payload.issuing_authority,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(f"Verification request {req.id} submitted by doctor {doctor.id}")
        return req

    async def get_doctor_verification_status(self, user: User) -> VerificationStatusResponse:
        """Retrieve current verification state and submitted documents."""
        doctor = await self.doc_repo.get_by_user_id(user.id)
        if not doctor:
            return VerificationStatusResponse(
                doctor_id=None,
                verification_status="not_applied",
                credentials=[],
                documents=[],
            )

        latest_req = await self.ver_repo.get_latest_request_for_doctor(doctor.id)

        documents_out = []
        if latest_req and latest_req.documents:
            for doc in latest_req.documents:
                # Generate temporary signed download URL for owner
                download_url = FileService.get_presigned_download_url(doc.document_key)
                documents_out.append(
                    VerificationDocumentItem(
                        id=doc.id,
                        document_type=doc.document_type,
                        original_name=doc.original_name,
                        mime_type=doc.mime_type,
                        size_bytes=doc.size_bytes,
                        uploaded_at=doc.uploaded_at,
                        download_url=download_url,
                    )
                )

        credentials_out = []
        if doctor.credentials:
            for cred in doctor.credentials:
                credentials_out.append(
                    {
                        "id": str(cred.id),
                        "credential_type": cred.credential_type.value,
                        "credential_number": cred.credential_number,
                        "issuing_authority": cred.issuing_authority,
                        "verification_status": cred.verification_status,
                        "submitted_at": cred.submitted_at.isoformat() if cred.submitted_at else None,
                    }
                )

        return VerificationStatusResponse(
            doctor_id=doctor.id,
            verification_status=doctor.verification_status,
            verified_at=doctor.verified_at,
            latest_request_id=latest_req.id if latest_req else None,
            latest_request_status=latest_req.status if latest_req else None,
            admin_notes=latest_req.admin_notes if latest_req else None,
            submitted_at=latest_req.submitted_at if latest_req else None,
            reviewed_at=latest_req.reviewed_at if latest_req else None,
            credentials=credentials_out,
            documents=documents_out,
        )

    # --- Admin Review Operations ---
    async def list_admin_queue(
        self,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[AdminVerificationQueueItem], int]:
        """Fetch pending verification queue items for administrator review."""
        req_status = None
        if status_filter:
            try:
                req_status = VerificationRequestStatus(status_filter)
            except ValueError:
                pass

        skip = (page - 1) * per_page
        requests, total = await self.ver_repo.list_admin_queue(
            status_filter=req_status,
            skip=skip,
            limit=per_page,
        )

        items = []
        for r in requests:
            doctor = r.doctor
            user = doctor.user if doctor else None
            cred = doctor.credentials[0] if doctor and doctor.credentials else None

            items.append(
                AdminVerificationQueueItem(
                    request_id=r.id,
                    doctor_id=doctor.id if doctor else uuid.uuid4(),
                    doctor_name=doctor.full_name if doctor else "Unknown Doctor",
                    doctor_slug=doctor.slug if doctor else "",
                    doctor_email=user.email if user else None,
                    doctor_phone=user.phone if user else None,
                    credential_type=cred.credential_type.value if cred else None,
                    credential_number=cred.credential_number if cred else None,
                    issuing_authority=cred.issuing_authority if cred else None,
                    status=r.status,
                    submitted_at=r.submitted_at,
                    documents_count=len(r.documents) if r.documents else 0,
                )
            )

        return items, total

    async def review_verification_request(
        self,
        admin_user: User,
        request_id: uuid.UUID,
        payload: AdminVerificationReviewRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> VerificationRequest:
        """
        Execute admin review decision: approve (grant badge), reject, request info, or suspend.
        Generates mandatory audit log.
        """
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only administrators can review verification requests.")

        req = await self.ver_repo.get_request_with_details(request_id)
        if not req:
            raise NotFoundError("Verification request not found.")

        now = datetime.now(timezone.utc)
        doctor = req.doctor
        req.admin_id = admin_user.id
        req.admin_notes = payload.admin_notes
        req.reviewed_at = now

        action = payload.action.lower()

        if action == "approve":
            req.status = VerificationRequestStatus.APPROVED
            doctor.verification_status = VerificationStatus.VERIFIED
            doctor.verified_at = now
            # Upgrade user role to DOCTOR upon verification approval
            if doctor.user:
                doctor.user.role = UserRole.DOCTOR
            else:
                user_record = await self.db.get(User, doctor.user_id)
                if user_record:
                    user_record.role = UserRole.DOCTOR

            # Update credentials
            for c in doctor.credentials:
                c.verification_status = "verified"
                c.verified_at = now
                c.verified_by = admin_user.id

            logger.info(f"✅ Doctor {doctor.id} APPROVED by admin {admin_user.id}. Role upgraded to DOCTOR. Badge granted.")

        elif action == "reject":
            req.status = VerificationRequestStatus.REJECTED
            doctor.verification_status = VerificationStatus.REJECTED
            if payload.rejection_reason:
                req.admin_notes = payload.rejection_reason
            for c in doctor.credentials:
                c.verification_status = "rejected"
            logger.info(f"❌ Doctor {doctor.id} REJECTED by admin {admin_user.id}. Reason: {payload.rejection_reason}")

        elif action == "request_info":
            req.status = VerificationRequestStatus.ADDITIONAL_INFO_REQUIRED
            doctor.verification_status = VerificationStatus.ADDITIONAL_INFO_REQUIRED

        elif action == "suspend":
            req.status = VerificationRequestStatus.REJECTED
            doctor.verification_status = VerificationStatus.SUSPENDED
            logger.warning(f"⚠️ Doctor {doctor.id} SUSPENDED by admin {admin_user.id}.")

        await self.db.flush()

        # Immutable Audit Log
        await self.audit_repo.log_action(
            action=f"VERIFICATION_{action.upper()}",
            resource_type="verification_request",
            actor_id=admin_user.id,
            resource_id=req.id,
            details={
                "doctor_id": str(doctor.id),
                "action": action,
                "admin_notes": payload.admin_notes,
                "rejection_reason": payload.rejection_reason,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return req
