"""Aggregated API v1 Router."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.admin_verification import router as admin_verification_router
from app.api.v1.auth import router as auth_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.doctor_profile import router as doctor_profile_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.health import router as health_router
from app.api.v1.hospitals import router as hospitals_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.posts import router as posts_router
from app.api.v1.search import router as search_router
from app.api.v1.verification import router as verification_router

api_v1_router = APIRouter(prefix="/api/v1")

# Register all sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(doctor_profile_router)
api_v1_router.include_router(verification_router)
api_v1_router.include_router(doctors_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(posts_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(hospitals_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(admin_verification_router)
