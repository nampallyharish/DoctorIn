"""Authentication REST API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    TokenResponse,
    UserProfileResponse,
    VerifyOTPRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user (Doctor, Patient, Hospital Admin)",
)
async def register(
    payload: RegisterRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account in pending verification state and send an OTP.
    """
    service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    user, identifier = await service.register_user(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
        background_tasks=background_tasks,
    )

    return APIResponse(
        success=True,
        data={
            "message": "Registration initiated. Verification code sent.",
            "identifier": identifier,
            "role": user.role,
        },
    )


@router.post(
    "/send-otp",
    response_model=APIResponse[dict],
    summary="Send or resend OTP",
)
async def send_otp(
    payload: SendOTPRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Send OTP code for login, registration, or verification. Rate-limited per identifier & IP.
    """
    service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    await service.send_otp(
        identifier=payload.identifier,
        purpose=payload.purpose,
        ip_address=ip_address,
        user_agent=user_agent,
        background_tasks=background_tasks,
    )

    return APIResponse(
        success=True,
        data={
            "message": "If the account exists or can be registered, a verification code was dispatched.",
        },
    )


@router.post(
    "/verify-otp",
    response_model=APIResponse[TokenResponse],
    summary="Verify OTP and obtain JWT tokens",
)
async def verify_otp(
    payload: VerifyOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify OTP code. On success, returns short-lived JWT access token and rotating refresh token.
    """
    service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    token_response = await service.verify_otp_and_login(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data=token_response,
    )


@router.post(
    "/reset-password",
    response_model=APIResponse[dict],
    summary="Reset or establish account password via verified OTP",
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Establish or reset password using verified OTP (purpose=password_reset).
    Allows existing accounts without a password hash to establish one safely.
    """
    service = AuthService(db)
    await service.reset_password(
        identifier=payload.identifier,
        otp=payload.otp,
        new_password=payload.new_password,
    )
    return APIResponse(
        success=True,
        data={"message": "Password updated successfully. You can now login with your new password."},
    )


@router.post(
    "/login",
    response_model=APIResponse[dict],
    summary="Password-based login (Triggers OTP)",
)
async def login(
    payload: LoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate using email/phone and password. If correct, sends an OTP.
    """
    service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    response_data = await service.login_with_password(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
        background_tasks=background_tasks,
    )

    return APIResponse(
        success=True,
        data=response_data,
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Refresh access token with refresh token rotation",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Rotate refresh token and issue new access token. Detects token reuse.
    """
    service = AuthService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    token_response = await service.refresh_access_token(
        raw_refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data=token_response,
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict],
    summary="Logout and revoke refresh token",
)
async def logout(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a single refresh token session.
    """
    service = AuthService(db)
    await service.logout(payload.refresh_token)

    return APIResponse(
        success=True,
        data={"message": "Logged out successfully."},
    )


@router.post(
    "/logout-all",
    response_model=APIResponse[dict],
    summary="Logout and revoke all active sessions",
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke all refresh token sessions across all devices for the authenticated user.
    """
    service = AuthService(db)
    await service.logout_all(current_user.id)

    return APIResponse(
        success=True,
        data={"message": "All sessions revoked successfully."},
    )


@router.get(
    "/me",
    response_model=APIResponse[UserProfileResponse],
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve authenticated user profile and verification status.
    """
    full_name = None
    profile_photo_url = None
    if current_user.patient_profile and current_user.patient_profile.display_name:
        full_name = current_user.patient_profile.display_name
    elif current_user.doctor_profile and current_user.doctor_profile.full_name:
        full_name = current_user.doctor_profile.full_name
        profile_photo_url = current_user.doctor_profile.profile_photo_url

    return APIResponse(
        success=True,
        data=UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            phone=current_user.phone,
            role=current_user.role,
            status=current_user.status.value,
            email_verified=current_user.email_verified,
            phone_verified=current_user.phone_verified,
            full_name=full_name,
            profile_photo_url=profile_photo_url,
        ),
    )

