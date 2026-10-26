"""Hospital and organization models."""

import enum
import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, SoftDeleteMixin


class HospitalAdminRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"


class HospitalVerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class HospitalType(str, enum.Enum):
    SUPER_SPECIALTY = "super_specialty"
    MULTI_SPECIALTY = "multi_specialty"
    GENERAL = "general"
    CLINIC = "clinic"
    RESEARCH_INSTITUTE = "research_institute"
    OTHER = "other"


class AffiliationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ENDED = "ended"


class JobEmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONSULTANT = "consultant"
    VISITING = "visiting"
    FELLOW = "fellow"


EmploymentType = JobEmploymentType



class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"


class JobApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Hospital(BaseModel, SoftDeleteMixin):
    __tablename__ = "hospitals"

    name: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(350), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    hospital_type: Mapped[HospitalType] = mapped_column(
        Enum(HospitalType, name="hospital_type_enum", values_callable=lambda x: [e.value for e in x]),
        default=HospitalType.GENERAL,
        nullable=False,
    )
    verification_status: Mapped[HospitalVerificationStatus] = mapped_column(
        Enum(HospitalVerificationStatus, name="hospital_verification_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=HospitalVerificationStatus.UNVERIFIED,
        nullable=False,
        index=True,
    )
    verified_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Organization details
    legal_entity_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year_established: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ownership_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Contact person
    contact_person_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_person_designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_person_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_person_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Facilities
    bed_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_emergency_services: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    admins = relationship("HospitalAdmin", back_populates="hospital", cascade="all, delete-orphan")
    departments = relationship("HospitalDepartment", back_populates="hospital", cascade="all, delete-orphan")
    doctors = relationship("HospitalDoctor", back_populates="hospital", cascade="all, delete-orphan")
    jobs = relationship("HospitalJobPost", back_populates="hospital", cascade="all, delete-orphan")


class HospitalAdmin(BaseModel):
    __tablename__ = "hospital_admins"
    __table_args__ = (
        UniqueConstraint("hospital_id", "user_id", name="uq_hospital_admin"),
    )

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[HospitalAdminRole] = mapped_column(
        Enum(HospitalAdminRole, name="hospital_admin_role_enum", values_callable=lambda x: [e.value for e in x]),
        default=HospitalAdminRole.ADMIN,
        nullable=False,
    )

    hospital = relationship("Hospital", back_populates="admins")
    user = relationship("User")


class HospitalDepartment(BaseModel):
    __tablename__ = "hospital_departments"

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    head_doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True
    )

    hospital = relationship("Hospital", back_populates="departments")


class HospitalDoctor(BaseModel):
    __tablename__ = "hospital_doctors"
    __table_args__ = (
        UniqueConstraint("hospital_id", "doctor_id", name="uq_hospital_doctor"),
    )

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospital_departments.id", ondelete="SET NULL"), nullable=True
    )
    designation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    joined_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    hospital = relationship("Hospital", back_populates="doctors")
    doctor = relationship("Doctor")


class HospitalJobPost(BaseModel):
    __tablename__ = "hospital_job_posts"

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    specialization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("specializations.id", ondelete="SET NULL"), nullable=True
    )
    minimum_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employment_type: Mapped[JobEmploymentType] = mapped_column(
        Enum(JobEmploymentType, name="job_employment_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=JobStatus.DRAFT,
        nullable=False,
    )
    application_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    hospital = relationship("Hospital", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job_post", cascade="all, delete-orphan")


class JobApplication(BaseModel):
    __tablename__ = "job_applications"
    __table_args__ = (
        UniqueConstraint("job_post_id", "doctor_id", name="uq_job_application"),
    )

    job_post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospital_job_posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[JobApplicationStatus] = mapped_column(
        Enum(JobApplicationStatus, name="job_application_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=JobApplicationStatus.SUBMITTED,
        nullable=False,
    )

    job_post = relationship("HospitalJobPost", back_populates="applications")
    doctor = relationship("Doctor")


# Aliases for compatibility
JobPosting = HospitalJobPost
JobPostingStatus = JobStatus
DoctorHospitalAffiliation = HospitalDoctor


