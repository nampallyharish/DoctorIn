"""Database Initialization & Seed Script.
Populates standard medical specialties, Indian metropolitan cities, and initial system admin.
"""

import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models.audit import City
from app.models.base import Base
from app.models.doctor import Specialization
from app.models.user import User, UserRole, UserStatus

SPECIALIZATIONS_SEED = [
    ("Cardiology", "cardiology", "Cardiovascular medicine, catheterization, and heart failure management"),
    ("Neurology", "neurology", "Brain, stroke, central nervous system, and neuro-disorders"),
    ("Oncology", "oncology", "Medical, surgical, and radiation oncology therapies"),
    ("Orthopedics", "orthopedics", "Joint replacements, spine surgery, and sports medicine"),
    ("Pediatrics", "pediatrics", "Neonatal care and child healthcare medicine"),
    ("Dermatology", "dermatology", "Clinical dermatology and cosmetology"),
    ("Gastroenterology", "gastroenterology", "Hepatology and GI endoscopy"),
    ("Radiology", "radiology", "Diagnostic MRI, CT, and interventional radiology"),
    ("Psychiatry", "psychiatry", "Clinical psychiatry and mental health"),
    ("General Surgery", "general-surgery", "Laparoscopy and trauma surgical interventions"),
]

CITIES_SEED = [
    ("Mumbai", "mumbai", "Maharashtra", "IND"),
    ("Delhi", "delhi", "Delhi", "IND"),
    ("Bengaluru", "bengaluru", "Karnataka", "IND"),
    ("Hyderabad", "hyderabad", "Telangana", "IND"),
    ("Chennai", "chennai", "Tamil Nadu", "IND"),
    ("Kolkata", "kolkata", "West Bengal", "IND"),
    ("Pune", "pune", "Maharashtra", "IND"),
    ("Ahmedabad", "ahmedabad", "Gujarat", "IND"),
]


async def init_and_seed():
    print("=" * 60)
    print("🏥 DOCTORIN — DATABASE INITIALIZATION & SEEDING")
    print("=" * 60)

    # 1. Create all tables
    print("\n▶ Ensuring all PostgreSQL tables exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables synced.")

    async with AsyncSessionLocal() as session:
        # 2. Seed Specializations
        print("\n▶ Seeding Medical Specializations...")
        for name, slug, desc in SPECIALIZATIONS_SEED:
            exists = await session.scalar(select(Specialization).where(Specialization.slug == slug))
            if not exists:
                session.add(Specialization(name=name, slug=slug, description=desc, is_active=True))
        await session.flush()
        print("✅ Medical Specializations seeded.")

        # 3. Seed Major Cities
        print("\n▶ Seeding Major Cities...")
        for name, slug, state, country in CITIES_SEED:
            exists = await session.scalar(select(City).where(City.slug == slug))
            if not exists:
                session.add(City(name=name, slug=slug, state=state, country=country, is_active=True))
        await session.flush()
        print("✅ Cities seeded.")

        # 4. Seed Root Administrator Account
        print("\n▶ Seeding Root Administrator Account...")
        admin_email = "admin@doctorin.app"
        admin_exists = await session.scalar(select(User).where(User.email == admin_email))
        if not admin_exists:
            admin_user = User(
                email=admin_email,
                phone="+910000000000",
                password_hash=hash_password("DoctorInAdminPass2026!"),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                email_verified=True,
                phone_verified=True,
            )
            session.add(admin_user)
            await session.flush()
            print(f"✅ Root Admin created: {admin_email}")
        else:
            print("ℹ️ Root Admin account already present.")

        await session.commit()

    print("\n" + "=" * 60)
    print("🎉 Database Initialization & Seeding Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(init_and_seed())
