"""Pydantic schemas for Hospitals, Departments, Affiliations, Job Postings, and Applications."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.doctor import VerificationStatus
from app.models.hospital import (
    AffiliationStatus,
    EmploymentType,
    HospitalType,
    JobApplicationStatus,
    JobPostingStatus,
)


# --- Department Schemas ---
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    head_doctor_id: uuid.UUID | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    hospital_id: uuid.UUID
    created_at: datetime


# --- Hospital Profile Schemas ---
class HospitalProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=300)
    tagline: str | None = Field(None, max_length=500)
    hospital_type: HospitalType | None = None
    about: str | None = Field(None, max_length=5000)
    website: str | None = Field(None, max_length=500)
    email: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    city_name: str | None = None
    total_beds: int | None = Field(None, ge=0)
    accreditations: list[str] | None = []


class HospitalResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    tagline: str | None = None
    hospital_type: HospitalType
    about: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line1: str | None = None
    city_name: str | None = None
    total_beds: int | None = None
    accreditations: list[str] = []
    verification_status: VerificationStatus
    verified_at: datetime | None = None
    logo_key: str | None = None
    departments: list[DepartmentResponse] = []
    created_at: datetime


# --- Affiliation Schemas ---
class AffiliationRequestCreate(BaseModel):
    hospital_id: uuid.UUID
    department_id: uuid.UUID | None = None
    designation: str = Field(..., min_length=2, max_length=200)
    start_date: date


class AffiliationResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    doctor_name: str
    doctor_slug: str
    doctor_headline: str | None = None
    hospital_id: uuid.UUID
    hospital_name: str
    department_name: str | None = None
    designation: str
    status: AffiliationStatus
    start_date: date
    created_at: datetime


# --- Job Postings Schemas ---
class JobPostingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    specialization_id: uuid.UUID | None = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    city_name: str | None = Field(None, max_length=100)
    min_experience_years: int = Field(0, ge=0, le=50)
    max_experience_years: int | None = Field(None, ge=0, le=50)
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "INR"
    description: str = Field(..., min_length=10, max_length=10000)
    requirements: str | None = None
    benefits: str | None = None
    application_deadline: date | None = None


class JobPostingResponse(BaseModel):
    id: uuid.UUID
    hospital_id: uuid.UUID
    hospital_name: str
    hospital_slug: str
    hospital_logo_key: str | None = None
    hospital_verified: bool = False
    title: str
    slug: str
    employment_type: EmploymentType
    city_name: str | None = None
    min_experience_years: int
    max_experience_years: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str
    description: str
    requirements: str | None = None
    benefits: str | None = None
    status: JobPostingStatus
    application_deadline: date | None = None
    views_count: int
    applications_count: int
    created_at: datetime


# --- Job Application Schemas ---
class JobApplicationCreate(BaseModel):
    cover_note: str | None = Field(None, max_length=2000)


class JobApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    doctor_id: uuid.UUID
    doctor_name: str
    doctor_slug: str
    doctor_headline: str | None = None
    doctor_verified: bool = False
    cover_note: str | None = None
    status: JobApplicationStatus
    applied_at: datetime


# --- Hospital Application & Verification Schemas ---
class HospitalDocumentItem(BaseModel):
    document_type: str = "hospital_license"
    document_key: str
    original_name: str
    mime_type: str = "application/pdf"
    size_bytes: int = 0


class HospitalApplicationRequest(BaseModel):
    # Hospital information
    name: str = Field(..., min_length=2, max_length=300)
    hospital_type: HospitalType = HospitalType.GENERAL
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    address: str | None = None
    city_name: str | None = None
    state: str | None = None
    country: str = "India"
    pincode: str | None = None
    year_established: int | None = None

    # Organization details
    legal_entity_name: str = Field(..., min_length=2, max_length=300)
    registration_number: str = Field(..., min_length=2, max_length=100)
    ownership_type: str | None = None
    accreditations: list[str] = []

    # Contact person / Authorized representative
    contact_person_name: str = Field(..., min_length=2, max_length=200)
    contact_person_designation: str = Field(..., min_length=2, max_length=100)
    contact_person_phone: str = Field(..., min_length=5, max_length=20)
    contact_person_email: str = Field(..., min_length=5, max_length=255)

    # Facilities
    departments: list[str] = []
    specializations: list[str] = []
    bed_count: int | None = Field(None, ge=0)
    has_emergency_services: bool = False

    # Documents
    documents: list[HospitalDocumentItem] = []


class HospitalVerificationStatusResponse(BaseModel):
    hospital_id: uuid.UUID | None = None
    hospital_name: str | None = None
    verification_status: str | None = None
    verified_at: date | None = None
    latest_request_id: uuid.UUID | None = None
    latest_request_status: str | None = None
    admin_notes: str | None = None
    rejection_reason: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    documents: list[dict] = []


class AdminHospitalVerificationQueueItem(BaseModel):
    request_id: uuid.UUID
    hospital_id: uuid.UUID
    hospital_name: str
    hospital_type: str
    legal_entity_name: str | None = None
    registration_number: str | None = None
    contact_person_name: str | None = None
    contact_person_email: str | None = None
    contact_person_phone: str | None = None
    city: str | None = None
    status: str
    submitted_at: datetime
    documents_count: int = 0

