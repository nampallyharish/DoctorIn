"""Verification requests and uploaded document models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class VerificationRequestStatus(str, enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationRequest(BaseModel):
    __tablename__ = "verification_requests"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[VerificationRequestStatus] = mapped_column(
        Enum(VerificationRequestStatus, name="verification_request_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=VerificationRequestStatus.PENDING,
        nullable=False,
        index=True,
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    doctor = relationship("Doctor")
    admin = relationship("User")
    documents = relationship("VerificationDocument", back_populates="verification_request", cascade="all, delete-orphan")


class VerificationDocument(BaseModel):
    __tablename__ = "verification_documents"

    verification_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    verification_request = relationship("VerificationRequest", back_populates="documents")


class HospitalVerificationRequest(BaseModel):
    __tablename__ = "hospital_verification_requests"

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[VerificationRequestStatus] = mapped_column(
        Enum(VerificationRequestStatus, name="hospital_verification_request_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=VerificationRequestStatus.PENDING,
        nullable=False,
        index=True,
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    hospital = relationship("Hospital")
    admin = relationship("User")
    documents = relationship("HospitalVerificationDocument", back_populates="verification_request", cascade="all, delete-orphan")


class HospitalVerificationDocument(BaseModel):
    __tablename__ = "hospital_verification_documents"

    verification_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospital_verification_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    verification_request = relationship("HospitalVerificationRequest", back_populates="documents")

