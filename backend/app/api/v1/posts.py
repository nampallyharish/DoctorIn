"""Social Feed Posts, Comments, Reactions, and Moderation REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse, MetaData
from app.schemas.post import (
    PostCommentCreate,
    PostCommentResponse,
    PostCreate,
    PostReactionCreate,
    PostReportCreate,
    PostResponse,
)
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Social Feed & Posts"])


@router.get(
    "/feed",
    response_model=APIResponse[list[PostResponse]],
    summary="Get paginated public medical feed",
)
async def get_feed(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve public medical posts feed."""
    service = PostService(db)
    posts, total = await service.get_feed(
        current_user_id=None,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        data=posts,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.post(
    "",
    response_model=APIResponse[PostResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Publish a professional update, case study, or research announcement",
)
async def create_post(
    payload: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Doctors and Hospital accounts can publish feed updates."""
    service = PostService(db)
    post = await service.create_post(current_user, payload)
    return APIResponse(success=True, data=post)


@router.delete(
    "/{post_id}",
    response_model=APIResponse[dict],
    summary="Delete own post",
)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a post by its author or administrator."""
    service = PostService(db)
    await service.delete_post(current_user, post_id)
    return APIResponse(success=True, data={"message": "Post deleted successfully."})


@router.post(
    "/{post_id}/reactions",
    response_model=APIResponse[dict],
    summary="Like/react to post (Like, Insightful, Support, Celebrate)",
)
async def react_to_post(
    post_id: uuid.UUID,
    payload: PostReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle reaction on post."""
    service = PostService(db)
    is_active, reaction = await service.toggle_reaction(current_user, post_id, payload)
    return APIResponse(
        success=True,
        data={
            "is_active": is_active,
            "reaction_type": reaction,
        },
    )


@router.get(
    "/{post_id}/comments",
    response_model=APIResponse[list[PostCommentResponse]],
    summary="List comments for a post",
)
async def list_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List comments on a post."""
    service = PostService(db)
    comments = await service.list_comments(post_id)
    return APIResponse(success=True, data=comments)


@router.post(
    "/{post_id}/comments",
    response_model=APIResponse[PostCommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to post",
)
async def add_comment(
    post_id: uuid.UUID,
    payload: PostCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment or threaded reply."""
    service = PostService(db)
    comment = await service.add_comment(current_user, post_id, payload)
    return APIResponse(success=True, data=comment)


@router.post(
    "/{post_id}/report",
    response_model=APIResponse[dict],
    summary="Report inappropriate, spam, or false medical claims for moderation",
)
async def report_post(
    post_id: uuid.UUID,
    payload: PostReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit post for content moderation review."""
    service = PostService(db)
    await service.report_post(current_user, post_id, payload)
    return APIResponse(
        success=True,
        data={"message": "Post reported. Our moderation team will inspect this content."},
    )
