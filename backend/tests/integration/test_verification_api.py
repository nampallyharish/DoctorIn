"""Integration tests for Multi-Role Onboarding, Doctor & Hospital Verification, and Admin Approvals."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.doctor import Doctor, VerificationStatus
from app.models.user import User, UserRole, UserStatus


@pytest.mark.asyncio
async def test_verification_status_unauthorized(async_client):
    """Test verification status endpoint rejects unauthenticated requests."""
    response = await async_client.get("/api/v1/doctors/me/verification/status")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_default_user_registration_as_user_role(async_client):
    """Test that registering without specifying a role defaults to UserRole.USER."""
    email = f"standard.user.{datetime.now().timestamp()}@example.com"
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Standard John Doe",
            "email": email,
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True

    # Check DB record
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.role == UserRole.USER


@pytest.mark.asyncio
async def test_doctor_application_and_admin_approval_promotes_role(async_client):
    """
    Test full doctor onboarding lifecycle:
    1. User created with role USER
    2. User checks status -> not_applied
    3. User submits Doctor Application
    4. Admin approves -> User role upgrades to DOCTOR, doctor.verification_status = VERIFIED
    """
    email = f"applicant.dr.{datetime.now().timestamp()}@example.com"

    # 1. Create active USER
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(user)

        admin = User(
            email=f"admin.{datetime.now().timestamp()}@hospital.org",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(user)
        await session.refresh(admin)
        user_id = user.id
        admin_id = admin.id

    user_token = create_access_token(subject=str(user_id), role="user")
    admin_token = create_access_token(subject=str(admin_id), role="admin")

    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Check initial doctor verification status
    status_res = await async_client.get(
        "/api/v1/doctors/me/verification/status", headers=user_headers
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["verification_status"] == "not_applied"

    # 3. User submits Doctor Application
    apply_payload = {
        "full_name": "Dr. Sarah Jenkins",
        "date_of_birth": "1990-05-15",
        "gender": "female",
        "specialization": "Cardiology",
        "sub_specialization": "Interventional Cardiology",
        "years_of_experience": 5,
        "current_hospital": "Metro Hospital",
        "designation": "Consultant Cardiologist",
        "areas_of_expertise": ["Angioplasty", "Echo"],
        "education": [
            {
                "degree": "MBBS",
                "institution": "All India Institute",
                "graduation_year": 2014,
            }
        ],
        "council_name": "National Medical Commission",
        "registration_number": f"NMC-{uuid.uuid4().hex[:6]}",
        "registration_state": "Delhi",
        "registration_country": "IND",
        "documents": [],
    }

    apply_res = await async_client.post(
        "/api/v1/doctors/me/verification/apply",
        headers=user_headers,
        json=apply_payload,
    )
    assert apply_res.status_code == 201
    apply_data = apply_res.json()
    assert apply_data["success"] is True
    request_id = apply_data["data"]["request_id"]
    assert apply_data["data"]["status"] == "pending"

    # 4. Admin reviews and approves the application
    approve_res = await async_client.put(
        f"/api/v1/admin/verification/{request_id}/review",
        headers=admin_headers,
        json={"action": "approve", "admin_notes": "All credentials verified with council records."},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["success"] is True

    # Verify that the user role has been promoted to DOCTOR in the database
    async with AsyncSessionLocal() as session:
        updated_user = await session.get(User, user_id)
        assert updated_user.role == UserRole.DOCTOR

        result = await session.execute(select(Doctor).where(Doctor.user_id == user_id))
        doctor = result.scalar_one()
        assert doctor.verification_status == VerificationStatus.VERIFIED


@pytest.mark.asyncio
async def test_doctor_application_rejection_stores_reason(async_client):
    """Test admin rejection records rejection reason and marks status as rejected."""
    email = f"rejected.dr.{datetime.now().timestamp()}@example.com"

    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(user)

        admin = User(
            email=f"admin2.{datetime.now().timestamp()}@hospital.org",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(user)
        await session.refresh(admin)
        user_id = user.id
        admin_id = admin.id

    user_token = create_access_token(subject=str(user_id), role="user")
    admin_token = create_access_token(subject=str(admin_id), role="admin")

    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Submit application
    apply_res = await async_client.post(
        "/api/v1/doctors/me/verification/apply",
        headers=user_headers,
        json={
            "full_name": "Dr. Unverified Doe",
            "specialization": "Pediatrics",
            "years_of_experience": 2,
            "council_name": "State Medical Council",
            "registration_number": "INVALID-12345",
        },
    )
    assert apply_res.status_code == 201
    request_id = apply_res.json()["data"]["request_id"]

    # Admin rejects
    reject_res = await async_client.put(
        f"/api/v1/admin/verification/{request_id}/review",
        headers=admin_headers,
        json={
            "action": "reject",
            "rejection_reason": "Registration number does not match council registry.",
        },
    )
    assert reject_res.status_code == 200

    # Verify status in DB and me/verification/status
    status_res = await async_client.get(
        "/api/v1/doctors/me/verification/status", headers=user_headers
    )
    assert status_res.status_code == 200
    data = status_res.json()["data"]
    assert data["verification_status"] == "rejected"
    assert "does not match" in data["admin_notes"]


@pytest.mark.asyncio
async def test_hospital_application_and_admin_approval(async_client):
    """Test full hospital application and admin verification review."""
    email = f"hospital.rep.{datetime.now().timestamp()}@hospital.org"

    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(user)

        admin = User(
            email=f"admin3.{datetime.now().timestamp()}@hospital.org",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(user)
        await session.refresh(admin)
        user_id = user.id
        admin_id = admin.id

    user_token = create_access_token(subject=str(user_id), role="user")
    admin_token = create_access_token(subject=str(admin_id), role="admin")

    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Check status before applying
    status_res = await async_client.get(
        "/api/v1/hospitals/me/verification/status", headers=user_headers
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["verification_status"] == "not_created"

    # Submit hospital application
    hosp_payload = {
        "name": f"City MultiSpecialty Hospital {uuid.uuid4().hex[:4]}",
        "hospital_type": "multi_specialty",
        "description": "Premier healthcare facility with tertiary care.",
        "email": email,
        "phone": "+919876543210",
        "legal_entity_name": "City Health Holdings Ltd",
        "registration_number": f"REG-HOSP-{uuid.uuid4().hex[:6]}",
        "ownership_type": "Private",
        "contact_person_name": "Dr. Representative",
        "contact_person_designation": "Director",
        "contact_person_phone": "+919876543210",
        "contact_person_email": email,
        "departments": ["Cardiology", "Neurology"],
        "bed_count": 250,
        "has_emergency_services": True,
        "documents": [],
    }

    apply_res = await async_client.post(
        "/api/v1/hospitals/apply",
        headers=user_headers,
        json=hosp_payload,
    )
    assert apply_res.status_code == 201
    apply_data = apply_res.json()
    assert apply_data["success"] is True
    request_id = apply_data["data"]["request_id"]
    assert apply_data["data"]["status"] == "pending"

    # Admin checks queue
    queue_res = await async_client.get(
        "/api/v1/admin/verification/hospitals/queue",
        headers=admin_headers,
    )
    assert queue_res.status_code == 200
    assert queue_res.json()["success"] is True
    assert len(queue_res.json()["data"]) >= 1

    # Admin approves hospital
    review_res = await async_client.put(
        f"/api/v1/admin/verification/hospitals/{request_id}/review",
        headers=admin_headers,
        json={"action": "approve", "admin_notes": "License validated with state medical board."},
    )
    assert review_res.status_code == 200
    assert review_res.json()["success"] is True

    # Verify hospital is verified and user promoted to HOSPITAL_ADMIN
    async with AsyncSessionLocal() as session:
        updated_user = await session.get(User, user_id)
        assert updated_user.role == UserRole.HOSPITAL_ADMIN


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_access_admin_queues(async_client):
    """Test regular user cannot access doctor or hospital admin verification queues."""
    user_token = create_access_token(subject=str(uuid.uuid4()), role="user")
    headers = {"Authorization": f"Bearer {user_token}"}

    doc_queue = await async_client.get("/api/v1/admin/verification/queue", headers=headers)
    assert doc_queue.status_code in [401, 403]

    hosp_queue = await async_client.get("/api/v1/admin/verification/hospitals/queue", headers=headers)
    assert hosp_queue.status_code in [401, 403]
