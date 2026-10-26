"""Pydantic schemas for Doctor Verification and Admin Credential Review."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.doctor import CredentialType, VerificationStatus
from app.models.verification import VerificationRequestStatus


class VerificationDocumentItem(BaseModel):
    id: uuid.UUID
    document_type: str
    original_name: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime
    download_url: str | None = None


class VerificationSubmitRequest(BaseModel):
    credential_type: CredentialType = CredentialType.MEDICAL_LICENSE
    credential_number: str = Field(..., min_length=3, max_length=100, description="Medical registration or license number")
    issuing_authority: str = Field(..., min_length=3, max_length=300, description="e.g. National Medical Commission, State Medical Council")
    issuing_country: str = Field(default="IND", min_length=2, max_length=3)
    issue_date: date | None = None
    expiry_date: date | None = None
    document_key: str | None = Field(None, max_length=500)
    document_original_name: str | None = Field(None, max_length=255)
    document_mime_type: str | None = Field(None, max_length=100)
    document_size_bytes: int | None = None
    supporting_notes: str | None = None


class VerificationDocumentUploadResponse(BaseModel):
    document_key: str
    document_original_name: str
    document_mime_type: str
    document_size_bytes: int
    message: str = "Document uploaded securely."


class EducationItem(BaseModel):
    degree: str
    institution: str
    graduation_year: int
    field_of_study: str | None = None


class DocumentItem(BaseModel):
    document_type: str = "medical_license"
    document_key: str
    original_name: str
    mime_type: str = "application/pdf"
    size_bytes: int = 0


class DoctorApplicationRequest(BaseModel):
    # Personal details
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = None
    profile_photo_key: str | None = None
    bio: str | None = None

    # Professional details
    specialization: str = Field(..., min_length=2, max_length=200)
    sub_specialization: str | None = None
    years_of_experience: int = Field(default=0, ge=0)
    current_hospital: str | None = None
    designation: str | None = None
    areas_of_expertise: list[str] = []

    # Education
    education: list[EducationItem] = []

    # Medical Registration
    council_name: str = Field(..., min_length=2, max_length=300)
    registration_number: str = Field(..., min_length=2, max_length=100)
    registration_state: str | None = None
    registration_country: str = "IND"
    registration_date: date | None = None

    # Documents
    documents: list[DocumentItem] = []


class VerificationStatusResponse(BaseModel):
    doctor_id: uuid.UUID | None = None
    verification_status: VerificationStatus | str | None = None
    verified_at: datetime | None = None
    latest_request_id: uuid.UUID | None = None
    latest_request_status: VerificationRequestStatus | None = None
    admin_notes: str | None = None
    rejection_reason: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    credentials: list[dict] = []
    documents: list[VerificationDocumentItem] = []


class AdminVerificationReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|request_info|suspend)$")
    admin_notes: str | None = Field(None, max_length=2000)
    rejection_reason: str | None = Field(None, max_length=500)


class AdminVerificationQueueItem(BaseModel):
    request_id: uuid.UUID
    doctor_id: uuid.UUID
    doctor_name: str
    doctor_slug: str
    doctor_email: str | None = None
    doctor_phone: str | None = None
    credential_type: str | None = None
    credential_number: str | None = None
    issuing_authority: str | None = None
    status: VerificationRequestStatus
    submitted_at: datetime
    documents_count: int
