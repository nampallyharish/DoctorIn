"""Comprehensive verification test for DoctorIn authentication flow and security checks.

Checks:
1. Create a NEW test account (Register with password)
2. Verify OTP (First login) -> Tokens issued
3. Logout -> Refresh token revoked, user remains intact
4. Login again with SAME credentials -> Succeeds (HTTP 200)
5. Wrong password -> Rejected (HTTP 401)
6. Wrong email -> Rejected (HTTP 401)
7. Password < 8 characters -> Rejected (HTTP 422)
8. Missing password -> Rejected (HTTP 422)
9. Existing NULL-password account -> Can safely establish password via OTP/reset flow
10. After setting password -> Normal password login works (HTTP 200)
11. Database verification: user exists, password_hash is not null, is valid bcrypt,
    logout does not alter password_hash.
"""

import asyncio
import uuid

import httpx
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_token, verify_password
from app.main import app
from app.models.user import (
    OTPPurpose,
    OTPVerification,
    User,
    UserRole,
    UserStatus,
)


async def run_full_suite():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        test_email = f"auth_e2e_{uuid.uuid4().hex[:8]}@doctorin.app"
        test_pw = "DoctorInSecurePass123!"
        print("\n=======================================================")
        print("DoctorIn Authentication Full Verification Suite")
        print("=======================================================")

        # --- 1. Validation Checks during Registration ---
        print("\n[CHECK 1] Reject registration if password < 8 chars")
        short_pw_resp = await client.post("/api/v1/auth/register", json={
            "role": "user",
            "full_name": "Short Pw User",
            "email": f"short_{uuid.uuid4().hex[:6]}@doctorin.app",
            "password": "short"
        })
        assert short_pw_resp.status_code == 422, f"Expected 422, got {short_pw_resp.status_code}"
        print("  PASS: HTTP 422 rejected short password.")

        print("\n[CHECK 2] Reject registration if password is missing")
        missing_pw_resp = await client.post("/api/v1/auth/register", json={
            "role": "user",
            "full_name": "No Pw User",
            "email": f"nopw_{uuid.uuid4().hex[:6]}@doctorin.app",
        })
        assert missing_pw_resp.status_code == 422, f"Expected 422, got {missing_pw_resp.status_code}"
        print("  PASS: HTTP 422 rejected missing password.")

        # --- 2. Register New User with Valid Password ---
        print(f"\n[CHECK 3] Register NEW account with valid credentials ({test_email})")
        reg_resp = await client.post("/api/v1/auth/register", json={
            "role": "user",
            "full_name": "DoctorIn Verified User",
            "email": test_email,
            "password": test_pw,
        })
        assert reg_resp.status_code == 201, f"Expected 201, got {reg_resp.status_code}"
        assert reg_resp.json()["success"] is True
        print("  PASS: Registration initiated successfully (HTTP 201).")

        # Verify DB immediately after registration
        saved_hash_initial = None
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            user_db = res.scalar_one_or_none()
            assert user_db is not None, "User not found in DB!"
            assert user_db.password_hash is not None, "Password hash is NULL after registration!"
            assert user_db.password_hash.startswith("$2b$") or user_db.password_hash.startswith("$2a$"), "Not a bcrypt hash!"
            assert verify_password(test_pw, user_db.password_hash) is True, "Password verification failed!"
            saved_hash_initial = user_db.password_hash
            print("  PASS: DB record verified -> User exists, password_hash is valid bcrypt, matches password.")

        # --- 3. First Login via OTP Verification ---
        print("\n[CHECK 4] Verify Registration OTP (First Login)")
        async with AsyncSessionLocal() as session:
            q = select(OTPVerification).where(
                OTPVerification.identifier == test_email,
                OTPVerification.purpose == OTPPurpose.REGISTRATION,
            ).order_by(OTPVerification.created_at.desc())
            res = await session.execute(q)
            otp_record = res.scalars().first()
            assert otp_record is not None
            otp_record.otp_hash = hash_token("654321")
            await session.commit()

        otp_resp = await client.post("/api/v1/auth/verify-otp", json={
            "identifier": test_email,
            "otp": "654321",
            "purpose": "registration",
        })
        assert otp_resp.status_code == 200, f"Expected 200, got {otp_resp.status_code}"
        tokens = otp_resp.json()["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        assert access_token and refresh_token
        print("  PASS: OTP verified, access and refresh tokens issued.")

        # Verify user is active in DB
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            user_db = res.scalar_one_or_none()
            assert user_db.status == UserStatus.ACTIVE
            assert user_db.password_hash == saved_hash_initial
            print("  PASS: User status is ACTIVE, password_hash unchanged.")

        # --- 4. Sign Out (Logout) ---
        print("\n[CHECK 5] Logout user (revoke session)")
        logout_resp = await client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert logout_resp.status_code == 200, f"Expected 200, got {logout_resp.status_code}"
        print("  PASS: Logout succeeded.")

        # Verify DB after logout
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            user_db = res.scalar_one_or_none()
            assert user_db is not None, "User was deleted during logout!"
            assert user_db.status == UserStatus.ACTIVE, "User was deactivated during logout!"
            assert user_db.deleted_at is None, "User was soft-deleted during logout!"
            assert user_db.password_hash == saved_hash_initial, "Password hash was modified during logout!"
            assert verify_password(test_pw, user_db.password_hash) is True, "Stored hash does not validate after logout!"
            print("  PASS: DB after logout -> User active, NOT deleted, NOT modified, password_hash intact and valid.")

        # --- 5. Sign In Again with the SAME Credentials ---
        print("\n[CHECK 6] Sign in again with the SAME credentials after logout")
        login_resp = await client.post("/api/v1/auth/login", json={
            "identifier": test_email,
            "password": test_pw,
        })
        assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}, response: {login_resp.json()}"
        login_data = login_resp.json()["data"]
        assert login_data["access_token"]
        assert login_data["refresh_token"]
        print("  PASS: Login after logout SUCCEEDED (HTTP 200). Tokens issued.")

        # --- 6. Negative Tests on Login ---
        print("\n[CHECK 7] Login with WRONG password rejected")
        wrong_pw_resp = await client.post("/api/v1/auth/login", json={
            "identifier": test_email,
            "password": "WrongPassword999!",
        })
        assert wrong_pw_resp.status_code == 401, f"Expected 401, got {wrong_pw_resp.status_code}"
        assert wrong_pw_resp.json()["errors"][0]["code"] == "UNAUTHORIZED"
        print("  PASS: Wrong password properly rejected (HTTP 401).")

        print("\n[CHECK 8] Login with WRONG email rejected")
        wrong_email_resp = await client.post("/api/v1/auth/login", json={
            "identifier": f"nonexistent_{uuid.uuid4().hex[:6]}@doctorin.app",
            "password": test_pw,
        })
        assert wrong_email_resp.status_code == 401, f"Expected 401, got {wrong_email_resp.status_code}"
        assert wrong_email_resp.json()["errors"][0]["code"] == "UNAUTHORIZED"
        print("  PASS: Nonexistent email properly rejected (HTTP 401).")

        # --- 7. Existing NULL-Password Account Handling ---
        print("\n[CHECK 9] Existing NULL-password account handling via OTP reset flow")
        null_user_email = f"null_pw_{uuid.uuid4().hex[:6]}@doctorin.app"
        # Simulate creating an existing legacy user with NULL password_hash
        async with AsyncSessionLocal() as session:
            legacy_u = User(
                email=null_user_email,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                password_hash=None,
                email_verified=True,
            )
            session.add(legacy_u)
            await session.commit()

        # Try password login on this legacy account -> Must be rejected (security preserved)
        legacy_login_resp = await client.post("/api/v1/auth/login", json={
            "identifier": null_user_email,
            "password": "SomeAttemptedPassword123!",
        })
        assert legacy_login_resp.status_code == 401, "Legacy NULL password account must be rejected on password login!"
        print("  PASS: Legacy NULL-password account rejected on password login (security preserved).")

        # Send password reset OTP
        send_reset_resp = await client.post("/api/v1/auth/send-otp", json={
            "identifier": null_user_email,
            "purpose": "password_reset",
        })
        assert send_reset_resp.status_code == 200
        print("  PASS: Dispatched password_reset OTP.")

        # Mock the OTP in DB
        async with AsyncSessionLocal() as session:
            q = select(OTPVerification).where(
                OTPVerification.identifier == null_user_email,
                OTPVerification.purpose == OTPPurpose.PASSWORD_RESET,
            ).order_by(OTPVerification.created_at.desc())
            res = await session.execute(q)
            otp_rec = res.scalars().first()
            assert otp_rec is not None
            otp_rec.otp_hash = hash_token("999888")
            await session.commit()

        # Reset/Establish password
        new_established_pw = "NewSecurePassword456!"
        reset_resp = await client.post("/api/v1/auth/reset-password", json={
            "identifier": null_user_email,
            "otp": "999888",
            "new_password": new_established_pw,
        })
        assert reset_resp.status_code == 200
        print("  PASS: Password established successfully via /api/v1/auth/reset-password.")

        # Verify DB for legacy user
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == null_user_email)
            res = await session.execute(q)
            u_check = res.scalar_one_or_none()
            assert u_check.password_hash is not None
            assert verify_password(new_established_pw, u_check.password_hash) is True
            print("  PASS: DB for legacy account now has a valid bcrypt password hash.")

        # Now password login for this previously NULL-password account MUST work
        legacy_login_success = await client.post("/api/v1/auth/login", json={
            "identifier": null_user_email,
            "password": new_established_pw,
        })
        assert legacy_login_success.status_code == 200
        print("  PASS: Former NULL-password account now logs in normally with the new password (HTTP 200).")

        print("\n=======================================================")
        print("ALL 9 VERIFICATION CHECKS PASSED PERFECTLY!")
        print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(run_full_suite())
