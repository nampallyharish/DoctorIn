"""Doctor and related professional profile database models."""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

TSVectorType = Text().with_variant(TSVECTOR, "postgresql")


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class CredentialType(str, enum.Enum):
    MEDICAL_LICENSE = "medical_license"
    REGISTRATION_NUMBER = "registration_number"
    BOARD_CERTIFICATION = "board_certification"
    SPECIALTY_CERTIFICATE = "specialty_certificate"
    OTHER = "other"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONSULTANT = "consultant"
    VISITING = "visiting"
    FELLOW = "fellow"
    RESIDENT = "resident"


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, index=True, nullable=False)
    headline: Mapped[str | None] = mapped_column(String(300), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    profile_photo_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    current_city_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    current_organization: Mapped[str | None] = mapped_column(String(300), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=VerificationStatus.UNVERIFIED,
        nullable=False,
        index=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_completion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    search_vector = mapped_column(TSVectorType, nullable=True)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    credentials = relationship("DoctorCredential", back_populates="doctor", cascade="all, delete-orphan")
    education = relationship("DoctorEducation", back_populates="doctor", cascade="all, delete-orphan", order_by="DoctorEducation.display_order")
    experience = relationship("DoctorExperience", back_populates="doctor", cascade="all, delete-orphan", order_by="DoctorExperience.display_order")
    specializations = relationship("DoctorSpecialization", back_populates="doctor", cascade="all, delete-orphan")
    achievements = relationship("DoctorAchievement", back_populates="doctor", cascade="all, delete-orphan", order_by="DoctorAchievement.display_order")
    publications = relationship("DoctorPublication", back_populates="doctor", cascade="all, delete-orphan", order_by="DoctorPublication.display_order")
    certifications = relationship("DoctorCertification", back_populates="doctor", cascade="all, delete-orphan")
    languages = relationship("DoctorLanguage", back_populates="doctor", cascade="all, delete-orphan")


class Specialization(BaseModel):
    __tablename__ = "specializations"

    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specializations.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    doctors = relationship("DoctorSpecialization", back_populates="specialization")


class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), primary_key=True
    )
    specialization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specializations.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    doctor = relationship("Doctor", back_populates="specializations")
    specialization = relationship("Specialization", back_populates="doctors")


class DoctorCredential(BaseModel):
    __tablename__ = "doctor_credentials"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    credential_type: Mapped[CredentialType] = mapped_column(
        Enum(CredentialType, name="credential_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    credential_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    issuing_authority: Mapped[str] = mapped_column(String(300), nullable=False)
    issuing_country: Mapped[str] = mapped_column(String(3), default="IND", nullable=False)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    doctor = relationship("Doctor", back_populates="credentials")


class DoctorEducation(BaseModel):
    __tablename__ = "doctor_education"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    institution: Mapped[str] = mapped_column(String(300), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    doctor = relationship("Doctor", back_populates="education")


class DoctorExperience(BaseModel):
    __tablename__ = "doctor_experience"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization: Mapped[str] = mapped_column(String(300), nullable=False)
    hospital_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True
    )
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType, name="employment_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    doctor = relationship("Doctor", back_populates="experience")


class DoctorAchievement(BaseModel):
    __tablename__ = "doctor_achievements"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    issuing_organization: Mapped[str | None] = mapped_column(String(300), nullable=True)
    achievement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    doctor = relationship("Doctor", back_populates="achievements")


class DoctorPublication(BaseModel):
    __tablename__ = "doctor_publications"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    journal: Mapped[str | None] = mapped_column(String(300), nullable=True)
    publication_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    doctor = relationship("Doctor", back_populates="publications")


class DoctorCertification(BaseModel):
    __tablename__ = "doctor_certifications"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(300), nullable=False)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    credential_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    doctor = relationship("Doctor", back_populates="certifications")


class DoctorLanguage(Base):
    __tablename__ = "doctor_languages"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(String(50), primary_key=True)
    proficiency: Mapped[str] = mapped_column(String(30), default="professional", nullable=False)

    doctor = relationship("Doctor", back_populates="languages")


class DoctorConnection(BaseModel):
    __tablename__ = "doctor_connections"
    __table_args__ = (
        UniqueConstraint("requester_id", "recipient_id", name="uq_doctor_connection"),
    )

    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ConnectionStatus] = mapped_column(
        Enum(ConnectionStatus, name="connection_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=ConnectionStatus.PENDING,
        nullable=False,
    )
