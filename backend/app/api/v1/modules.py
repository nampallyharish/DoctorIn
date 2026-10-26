"""Posts, Conversations, Hospitals, and Admin scaffolds for Phase 1."""

from fastapi import APIRouter

from app.schemas.common import APIResponse

search_router = APIRouter(prefix="/search", tags=["Search"])
posts_router = APIRouter(prefix="/posts", tags=["Posts"])
conversations_router = APIRouter(prefix="/conversations", tags=["Conversations"])
hospitals_router = APIRouter(prefix="/hospitals", tags=["Hospitals"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@search_router.get("/doctors", response_model=APIResponse[list])
async def search_doctors():
    return APIResponse(success=True, data=[])


@posts_router.get("/feed", response_model=APIResponse[list])
async def get_feed():
    return APIResponse(success=True, data=[])


@conversations_router.get("", response_model=APIResponse[list])
async def list_conversations():
    return APIResponse(success=True, data=[])


@hospitals_router.get("", response_model=APIResponse[list])
async def list_hospitals():
    return APIResponse(success=True, data=[])


@admin_router.get("/dashboard/stats", response_model=APIResponse[dict])
async def get_admin_stats():
    return APIResponse(success=True, data={"total_users": 0, "total_doctors": 0})
