"""Post Repository for social feed, media, comments, reactions, and reports."""

import uuid

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import Report, ReportReason, ReportStatus, TargetType
from app.models.post import (
    AuthorType,
    MediaType,
    Post,
    PostComment,
    PostMedia,
    PostReaction,
    PostType,
    PostVisibility,
    ReactionType,
)
from app.models.user import User
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Data access repository for social feed posts, reactions, comments, and reports."""

    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_post_with_details(self, post_id: uuid.UUID) -> Post | None:
        """Fetch single post with author, media, comments, and reactions."""
        query = (
            select(Post)
            .where(Post.id == post_id, Post.deleted_at.is_(None))
            .options(
                selectinload(Post.author).selectinload(User.doctor_profile),
                selectinload(Post.media),
                selectinload(Post.comments).selectinload(PostComment.author).selectinload(User.doctor_profile),
                selectinload(Post.reactions),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_feed(
        self,
        user_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Post], int]:
        """Fetch paginated public feed posts ordered by creation date."""
        query = (
            select(Post)
            .where(
                Post.deleted_at.is_(None),
                Post.is_moderated.is_(False),
                Post.visibility == PostVisibility.PUBLIC,
            )
            .options(
                selectinload(Post.author).selectinload(User.doctor_profile),
                selectinload(Post.media),
                selectinload(Post.reactions),
            )
            .order_by(desc(Post.is_pinned), desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )

        count_query = select(func.count(Post.id)).where(
            Post.deleted_at.is_(None),
            Post.is_moderated.is_(False),
            Post.visibility == PostVisibility.PUBLIC,
        )

        results = await self.session.execute(query)
        total = await self.session.scalar(count_query) or 0

        return list(results.scalars().all()), total

    async def create_post(
        self,
        author_id: uuid.UUID,
        author_type: AuthorType,
        content: str,
        post_type: PostType = PostType.TEXT,
        visibility: PostVisibility = PostVisibility.PUBLIC,
        media_keys: list[str] | None = None,
    ) -> Post:
        """Create new post with optional media attachments."""
        post = Post(
            author_id=author_id,
            author_type=author_type,
            content=content,
            post_type=post_type,
            visibility=visibility,
        )
        self.session.add(post)
        await self.session.flush()

        if media_keys:
            for idx, key in enumerate(media_keys):
                media = PostMedia(
                    post_id=post.id,
                    media_key=key,
                    media_type=MediaType.IMAGE,
                    display_order=idx,
                )
                self.session.add(media)

        await self.session.flush()
        return await self.get_post_with_details(post.id)

    async def toggle_reaction(
        self,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction_type: ReactionType = ReactionType.LIKE,
    ) -> tuple[bool, str]:
        """
        Toggle or update reaction on a post.
        Returns (is_active, reaction_type).
        """
        query = select(PostReaction).where(
            PostReaction.post_id == post_id, PostReaction.user_id == user_id
        )
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()

        post = await self.get_by_id(post_id)
        if not post:
            return False, ""

        if existing:
            if existing.reaction_type == reaction_type:
                # Remove reaction
                await self.session.delete(existing)
                post.reaction_count = max(0, post.reaction_count - 1)
                await self.session.flush()
                return False, ""
            else:
                # Update reaction type
                existing.reaction_type = reaction_type
                await self.session.flush()
                return True, reaction_type.value
        else:
            # Create new reaction
            reaction = PostReaction(
                post_id=post_id,
                user_id=user_id,
                reaction_type=reaction_type,
            )
            self.session.add(reaction)
            post.reaction_count += 1
            await self.session.flush()
            return True, reaction_type.value

    async def add_comment(
        self,
        post_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        parent_comment_id: uuid.UUID | None = None,
    ) -> PostComment:
        """Add comment to post and increment comment counter."""
        comment = PostComment(
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )
        self.session.add(comment)

        post = await self.get_by_id(post_id)
        if post:
            post.comment_count += 1

        await self.session.flush()
        return comment

    async def list_comments(self, post_id: uuid.UUID) -> list[PostComment]:
        """Fetch comments for a post ordered by timestamp."""
        query = (
            select(PostComment)
            .where(
                PostComment.post_id == post_id,
                PostComment.deleted_at.is_(None),
                PostComment.is_moderated.is_(False),
            )
            .options(
                selectinload(PostComment.author).selectinload(User.doctor_profile),
            )
            .order_by(PostComment.created_at.asc())
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def create_report(
        self,
        reporter_id: uuid.UUID,
        post_id: uuid.UUID,
        reason: str,
        description: str | None = None,
    ) -> Report:
        """Submit a content moderation report for a post."""
        report = Report(
            reporter_id=reporter_id,
            target_type=TargetType.POST,
            target_id=post_id,
            reason=ReportReason(reason),
            description=description,
            status=ReportStatus.PENDING,
        )
        self.session.add(report)
        await self.session.flush()
        return report
