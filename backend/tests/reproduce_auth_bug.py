import asyncio
import uuid

import httpx
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_token, verify_password
from app.main import app
from app.models.user import OTPPurpose, OTPVerification, User


async def main():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        test_email = f"test_auth_{uuid.uuid4().hex[:8]}@doctorin.app"
        test_pw = "DoctorInSecurePass123!"
        print("\n==========================================")
        print(f"Testing Flow for: {test_email} / {test_pw}")
        print("==========================================")

        # 1. Register
        print("\n--- STEP 1: Registration ---")
        reg_resp = await client.post("/api/v1/auth/register", json={
            "role": "user",
            "full_name": "Test User",
            "email": test_email,
            "password": test_pw
        })
        print(f"Register status: {reg_resp.status_code}, response: {reg_resp.json()}")

        # 2. Check DB after registration
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            u = res.scalar_one_or_none()
            print(f"User in DB after reg: {u}")
            if u:
                print(f"  status: {u.status}, pw_hash: {u.password_hash}")
                print(f"  verify_password matches test_pw? {verify_password(test_pw, u.password_hash)}")

        # 3. Simulate OTP verification (first login)
        print("\n--- STEP 2: Verify OTP (first login) ---")
        async with AsyncSessionLocal() as session:
            q = select(OTPVerification).where(
                OTPVerification.identifier == test_email,
                OTPVerification.purpose == OTPPurpose.REGISTRATION
            )
            res = await session.execute(q)
            otp_rec = res.scalars().first()
            if otp_rec:
                otp_rec.otp_hash = hash_token("123456")
                await session.commit()
                print("Set test OTP to 123456")

        otp_resp = await client.post("/api/v1/auth/verify-otp", json={
            "identifier": test_email,
            "otp": "123456",
            "purpose": "registration"
        })
        print(f"Verify OTP status: {otp_resp.status_code}, response: {otp_resp.json()}")
        tokens = otp_resp.json().get("data", {})
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        print(f"Got tokens: access_token={bool(access_token)}, refresh_token={bool(refresh_token)}")

        # 4. Check DB after OTP verification
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            u = res.scalar_one_or_none()
            print(f"User in DB after OTP: status={u.status}, pw_hash={u.password_hash}")

        # 5. Logout
        print("\n--- STEP 3: Logout ---")
        logout_resp = await client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token
        })
        print(f"Logout status: {logout_resp.status_code}, response: {logout_resp.json()}")

        # 6. Check DB after logout
        async with AsyncSessionLocal() as session:
            q = select(User).where(User.email == test_email)
            res = await session.execute(q)
            u = res.scalar_one_or_none()
            print(f"User in DB after logout: {u}")
            if u:
                print(f"  status: {u.status}, pw_hash: {u.password_hash}")
                print(f"  deleted_at: {u.deleted_at}")
                print(f"  verify_password matches test_pw? {verify_password(test_pw, u.password_hash)}")

        # 7. Try to login again with same credentials!
        print("\n--- STEP 4: Login again with same credentials ---")
        login_resp = await client.post("/api/v1/auth/login", json={
            "identifier": test_email,
            "password": test_pw
        })
        print(f"Login again status: {login_resp.status_code}, response: {login_resp.json()}")

if __name__ == "__main__":
    asyncio.run(main())
