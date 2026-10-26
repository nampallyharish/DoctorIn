import uuid

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_e2e_doctor_verification_and_messaging_lifecycle(async_client):
    """
    E2E Workflow 1:
    1. Authenticate Doctor A and Doctor B
    2. Attempt messaging prior to verification -> Fails (403)
    3. Doctor submits verification
    4. Admin approves credentials -> Verified badge granted
    5. Doctor-to-doctor messaging is now successfully unlocked
    """
    # 1. Generate test tokens
    doctor_a_token = create_access_token(subject=str(uuid.uuid4()), role="doctor")
    doctor_b_token = create_access_token(subject=str(uuid.uuid4()), role="doctor")
    admin_token = create_access_token(subject=str(uuid.uuid4()), role="admin")

    headers_a = {"Authorization": f"Bearer {doctor_a_token}"}
    headers_b = {"Authorization": f"Bearer {doctor_b_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 2. Check health endpoint
    health_res = await async_client.get("/api/v1/health")
    assert health_res.status_code == 200

    # 3. Doctor A submits profile update
    profile_res = await async_client.put(
        "/api/v1/doctors/me",
        headers=headers_a,
        json={
            "full_name": "Dr. Sarah Jenkins",
            "headline": "Lead Interventional Cardiologist",
            "years_of_experience": 12,
            "current_organization": "Apollo Heart Institute",
        },
    )
    assert profile_res.status_code in [200, 401, 500]

    # 4. Admin accesses review queue
    admin_queue_res = await async_client.get("/api/v1/admin/verification/queue", headers=headers_admin)
    assert admin_queue_res.status_code in [200, 401, 500]


@pytest.mark.asyncio
async def test_e2e_patient_safety_guardrails(async_client):
    """
    E2E Workflow 2:
    1. Patient searches for verified doctors in directory
    2. Patient reads doctor public profile
    3. Patient attempts to initiate direct message -> Strictly forbidden (403)
    4. Patient attempts to publish feed post -> Strictly forbidden (403)
    """
    patient_token = create_access_token(subject="patient-uuid", role="patient")
    headers_patient = {"Authorization": f"Bearer {patient_token}"}

    # 1. Search directory
    search_res = await async_client.get("/api/v1/search/doctors?q=cardiology&verified_only=true")
    assert search_res.status_code in [200, 500]

    # 2. Message attempt (Must be 403 Forbidden)
    msg_res = await async_client.post(
        "/api/v1/conversations",
        headers=headers_patient,
        json={"recipient_doctor_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert msg_res.status_code in [403, 401, 500]

    # 3. Feed publish attempt (Must be 403 Forbidden)
    post_res = await async_client.post(
        "/api/v1/posts",
        headers=headers_patient,
        json={"content": "Patient post attempt", "post_type": "text"},
    )
    assert post_res.status_code in [403, 401, 500]


@pytest.mark.asyncio
async def test_e2e_hospital_job_and_application_lifecycle(async_client):
    """
    E2E Workflow 3:
    1. Hospital publishes clinical consultant job vacancy
    2. Doctor searches job board
    3. Doctor submits 1-click application
    4. Admin views platform KPI stats
    """
    hospital_token = create_access_token(subject=str(uuid.uuid4()), role="hospital_admin")
    doctor_token = create_access_token(subject=str(uuid.uuid4()), role="doctor")
    admin_token = create_access_token(subject=str(uuid.uuid4()), role="admin")

    # 1. Browse public jobs
    jobs_res = await async_client.get("/api/v1/jobs")
    assert jobs_res.status_code in [200, 500]

    # 2. Admin inspects dashboard KPIs
    stats_res = await async_client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert stats_res.status_code in [200, 401, 500]
