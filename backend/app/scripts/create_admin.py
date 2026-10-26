"""CLI Script to create a secure Admin account."""

import asyncio
import getpass
import re
import sys
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus


async def create_admin():
    """Interactive command-line utility to provision an admin user."""
    print("=" * 50)
    print("DoctorIn Secure Admin Setup")
    print("=" * 50)

    try:
        email = input("Admin Email: ").strip().lower()
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("❌ Invalid email format.")
            sys.exit(1)

        password = getpass.getpass("Admin Password: ").strip()
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long.")
            sys.exit(1)

        confirm_password = getpass.getpass("Confirm Password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match.")
            sys.exit(1)

        full_name = input("Admin Full Name (Optional): ").strip()

        async with AsyncSessionLocal() as session:
            # Check if user already exists
            result = await session.execute(
                select(User).where((User.email == email) & (User.deleted_at.is_(None)))
            )
            existing_user = result.scalars().first()

            if existing_user:
                if existing_user.role == UserRole.ADMIN:
                    print(f"✅ Admin account for '{email}' already exists.")
                    sys.exit(0)
                else:
                    print(f"❌ User '{email}' exists but is not an admin. Cannot overwrite role securely.")
                    sys.exit(1)

            # Create new admin user
            admin_user = User(
                email=email,
                password_hash=get_password_hash(password),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                email_verified=True,
                created_at=datetime.now(timezone.utc),
            )
            session.add(admin_user)
            await session.commit()

            print("=" * 50)
            print(f"✅ Admin account successfully created for '{email}'!")
            print("You can now login at /login/admin using these credentials.")
            print("=" * 50)

    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error creating admin: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin())
