"""Pydantic schemas for Doctor profile and sub-resources."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.doctor import (
    EmploymentType,
    Gender,
    VerificationStatus,
)

# --- Sub-resource Schemas ---

class EducationBase(BaseModel):
    institution: str = Field(..., min_length=2, max_length=300)
    degree: str = Field(..., min_length=2, max_length=200)
    field_of_study: str | None = Field(None, max_length=200)
    start_year: int = Field(..., ge=1950, le=2100)
    end_year: int | None = Field(None, ge=1950, le=2100)
    grade: str | None = Field(None, max_length=50)
    description: str | None = None
    display_order: int = 0


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime


class ExperienceBase(BaseModel):
    organization: str = Field(..., min_length=2, max_length=300)
    hospital_id: uuid.UUID | None = None
    job_title: str = Field(..., min_length=2, max_length=200)
    employment_type: EmploymentType | None = EmploymentType.FULL_TIME
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    city: str | None = Field(None, max_length=100)
    description: str | None = None
    display_order: int = 0


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime


class SpecializationItem(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    is_primary: bool = False


class SpecializationAddRequest(BaseModel):
    specialization_id: uuid.UUID
    is_primary: bool = False


class AchievementBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: str | None = None
    issuing_organization: str | None = Field(None, max_length=300)
    achievement_date: date | None = None
    display_order: int = 0


class AchievementCreate(AchievementBase):
    pass


class AchievementResponse(AchievementBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    journal: str | None = Field(None, max_length=300)
    publication_url: str | None = Field(None, max_length=1000)
    doi: str | None = Field(None, max_length=100)
    publication_date: date | None = None
    abstract: str | None = None
    authors: str | None = None
    display_order: int = 0


class PublicationCreate(PublicationBase):
    pass


class PublicationResponse(PublicationBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime


class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=300)
    issuing_organization: str = Field(..., min_length=2, max_length=300)
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None


class CertificationResponse(CertificationCreate):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime


class LanguageCreate(BaseModel):
    language: str = Field(..., min_length=2, max_length=50)
    proficiency: str = "professional"


# --- Doctor Profile Schemas ---

class DoctorProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200)
    headline: str | None = Field(None, max_length=300)
    date_of_birth: date | None = None
    gender: Gender | None = None
    bio: str | None = Field(None, max_length=3000)
    years_of_experience: int | None = Field(None, ge=0, le=75)
    current_organization: str | None = Field(None, max_length=300)
    website: str | None = Field(None, max_length=500)
    current_city_id: uuid.UUID | None = None


class DoctorProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    slug: str
    headline: str | None = None
    bio: str | None = None
    years_of_experience: int | None = None
    current_organization: str | None = None
    website: str | None = None
    profile_photo_key: str | None = None
    verification_status: VerificationStatus
    verified_at: datetime | None = None
    profile_completion: int
    education: list[EducationResponse] = []
    experience: list[ExperienceResponse] = []
    specializations: list[SpecializationItem] = []
    achievements: list[AchievementResponse] = []
    publications: list[PublicationResponse] = []
    certifications: list[CertificationResponse] = []
    languages: list[LanguageCreate] = []
    created_at: datetime
    updated_at: datetime


class DoctorPublicProfileResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    slug: str
    headline: str | None = None
    bio: str | None = None
    years_of_experience: int | None = None
    current_organization: str | None = None
    profile_photo_key: str | None = None
    verification_status: VerificationStatus
    verified_at: datetime | None = None
    education: list[EducationResponse] = []
    experience: list[ExperienceResponse] = []
    specializations: list[SpecializationItem] = []
    achievements: list[AchievementResponse] = []
    publications: list[PublicationResponse] = []
    certifications: list[CertificationResponse] = []
    languages: list[LanguageCreate] = []
