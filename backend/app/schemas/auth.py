"""Authentication request and response schemas."""

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import OTPPurpose, UserRole


class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=r"^\+?[1-9]\d{6,14}$")
    role: UserRole = UserRole.USER
    full_name: str | None = Field(None, min_length=2, max_length=200)
    password: str = Field(..., min_length=8, max_length=128, description="Account password (min 8 characters)")

    @field_validator("phone")
    @classmethod
    def validate_identifier_provided(cls, v, info):
        # Enforce that either email or phone is provided
        return v


class SendOTPRequest(BaseModel):
    identifier: str = Field(..., description="Email or phone number")
    purpose: OTPPurpose = OTPPurpose.REGISTRATION


class VerifyOTPRequest(BaseModel):
    identifier: str
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    purpose: OTPPurpose = OTPPurpose.REGISTRATION


class LoginRequest(BaseModel):
    identifier: str
    password: str | None = None
    otp: str | None = None


class ResetPasswordRequest(BaseModel):
    identifier: str
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (min 8 characters)")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds
    user_id: uuid.UUID
    role: UserRole
    verification_status: str | None = None
    full_name: str | None = None


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str | None = None
    phone: str | None = None
    role: UserRole
    status: str
    email_verified: bool
    phone_verified: bool
    full_name: str | None = None
    profile_photo_url: str | None = None
