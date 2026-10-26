"""Post Business Logic Service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.doctor import VerificationStatus
from app.models.post import AuthorType, Post
from app.models.user import User, UserRole
from app.repositories.post_repo import PostRepository
from app.schemas.post import (
    PostCommentCreate,
    PostCommentResponse,
    PostCreate,
    PostMediaItem,
    PostReactionCreate,
    PostReportCreate,
    PostResponse,
)


class PostService:
    """Coordinates social feed posts, interactions, comments, and reports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PostRepository(db)

    def _format_post_response(self, post: Post, current_user_id: uuid.UUID | None = None) -> PostResponse:
        author = post.author
        doctor_profile = author.doctor_profile if author else None

        author_name = "Medical Professional"
        author_slug = None
        author_headline = None
        author_avatar = None
        author_verified = False

        if doctor_profile:
            author_name = doctor_profile.full_name
            author_slug = doctor_profile.slug
            author_headline = doctor_profile.headline
            author_avatar = doctor_profile.profile_photo_key
            author_verified = doctor_profile.verification_status == VerificationStatus.VERIFIED
        elif author:
            author_name = author.email or "User"

        # Check current user's reaction
        user_reaction = None
        if current_user_id and post.reactions:
            for r in post.reactions:
                if r.user_id == current_user_id:
                    user_reaction = r.reaction_type.value
                    break

        media_items = [
            PostMediaItem(
                id=m.id,
                media_key=m.media_key,
                media_type=m.media_type,
                original_name=m.original_name,
            )
            for m in post.media
        ]

        return PostResponse(
            id=post.id,
            author_id=post.author_id,
            author_type=post.author_type,
            author_name=author_name,
            author_slug=author_slug,
            author_headline=author_headline,
            author_avatar_key=author_avatar,
            author_verified=author_verified,
            content=post.content,
            post_type=post.post_type,
            visibility=post.visibility,
            reaction_count=post.reaction_count,
            comment_count=post.comment_count,
            user_reaction=user_reaction,
            is_pinned=post.is_pinned,
            media=media_items,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    async def get_feed(
        self,
        current_user_id: uuid.UUID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PostResponse], int]:
        """Fetch paginated feed posts with formatted author cards and reactions."""
        skip = (page - 1) * per_page
        posts, total = await self.repo.get_feed(
            user_id=current_user_id,
            skip=skip,
            limit=per_page,
        )
        formatted = [self._format_post_response(p, current_user_id) for p in posts]
        return formatted, total

    async def create_post(self, user: User, payload: PostCreate) -> PostResponse:
        """Doctors and Hospitals can publish posts."""
        if user.role not in [UserRole.DOCTOR, UserRole.HOSPITAL_ADMIN, UserRole.ADMIN]:
            raise ForbiddenError("Only doctors and hospitals can publish feed updates.")

        author_type = AuthorType.DOCTOR if user.role == UserRole.DOCTOR else AuthorType.HOSPITAL
        post = await self.repo.create_post(
            author_id=user.id,
            author_type=author_type,
            content=payload.content,
            post_type=payload.post_type,
            visibility=payload.visibility,
            media_keys=payload.media_keys,
        )
        return self._format_post_response(post, user.id)

    async def delete_post(self, user: User, post_id: uuid.UUID) -> bool:
        """Delete post (author or admin only)."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post not found.")

        if post.author_id != user.id and user.role != UserRole.ADMIN:
            raise ForbiddenError("You cannot delete another user's post.")

        return await self.repo.delete(post_id)

    async def toggle_reaction(
        self, user: User, post_id: uuid.UUID, payload: PostReactionCreate
    ) -> tuple[bool, str]:
        """React to post (any authenticated user)."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post not found.")

        return await self.repo.toggle_reaction(
            post_id=post_id,
            user_id=user.id,
            reaction_type=payload.reaction_type,
        )

    async def add_comment(
        self, user: User, post_id: uuid.UUID, payload: PostCommentCreate
    ) -> PostCommentResponse:
        """Add comment to post."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post not found.")

        comment = await self.repo.add_comment(
            post_id=post_id,
            author_id=user.id,
            content=payload.content,
            parent_comment_id=payload.parent_comment_id,
        )

        doc = user.doctor_profile
        author_name = doc.full_name if doc else (user.email or "User")
        author_verified = doc.verification_status == VerificationStatus.VERIFIED if doc else False

        return PostCommentResponse(
            id=comment.id,
            post_id=post_id,
            author_id=user.id,
            author_name=author_name,
            author_headline=doc.headline if doc else None,
            author_verified=author_verified,
            content=comment.content,
            parent_comment_id=comment.parent_comment_id,
            created_at=comment.created_at,
        )

    async def list_comments(self, post_id: uuid.UUID) -> list[PostCommentResponse]:
        """List comments for a post."""
        comments = await self.repo.list_comments(post_id)
        out = []
        for c in comments:
            doc = c.author.doctor_profile if c.author else None
            author_name = doc.full_name if doc else (c.author.email if c.author else "User")
            author_verified = doc.verification_status == VerificationStatus.VERIFIED if doc else False

            out.append(
                PostCommentResponse(
                    id=c.id,
                    post_id=c.post_id,
                    author_id=c.author_id,
                    author_name=author_name,
                    author_headline=doc.headline if doc else None,
                    author_verified=author_verified,
                    content=c.content,
                    parent_comment_id=c.parent_comment_id,
                    created_at=c.created_at,
                )
            )
        return out

    async def report_post(self, user: User, post_id: uuid.UUID, payload: PostReportCreate):
        """Submit post report for moderation."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post not found.")

        return await self.repo.create_report(
            reporter_id=user.id,
            post_id=post_id,
            reason=payload.reason,
            description=payload.description,
        )
