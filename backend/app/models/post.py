"""Social feed posts, media, comments, and reactions models."""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, SoftDeleteMixin


class AuthorType(str, enum.Enum):
    DOCTOR = "doctor"
    HOSPITAL = "hospital"


class PostVisibility(str, enum.Enum):
    PUBLIC = "public"
    CONNECTIONS_ONLY = "connections_only"
    PRIVATE = "private"


class PostType(str, enum.Enum):
    TEXT = "text"
    ARTICLE = "article"
    ACHIEVEMENT = "achievement"
    PUBLICATION = "publication"
    CASE_STUDY = "case_study"


class MediaType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    LINK = "link"


class ReactionType(str, enum.Enum):
    LIKE = "like"
    INSIGHTFUL = "insightful"
    SUPPORT = "support"
    CELEBRATE = "celebrate"


class Post(BaseModel, SoftDeleteMixin):
    __tablename__ = "posts"

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_type: Mapped[AuthorType] = mapped_column(
        Enum(AuthorType, name="author_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    visibility: Mapped[PostVisibility] = mapped_column(
        Enum(PostVisibility, name="post_visibility_enum", values_callable=lambda x: [e.value for e in x]),
        default=PostVisibility.PUBLIC,
        nullable=False,
    )
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type_enum", values_callable=lambda x: [e.value for e in x]),
        default=PostType.TEXT,
        nullable=False,
    )
    reaction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moderation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    author = relationship("User")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan", order_by="PostMedia.display_order")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan", order_by="PostComment.created_at")
    reactions = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")


class PostMedia(BaseModel):
    __tablename__ = "post_media"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_key: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType, name="media_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    post = relationship("Post", back_populates="media")


class PostComment(BaseModel, SoftDeleteMixin):
    __tablename__ = "post_comments"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User")
    replies = relationship("PostComment", backref="parent_comment", remote_side="PostComment.id")


class PostReaction(BaseModel):
    __tablename__ = "post_reactions"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_reaction"),
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reaction_type: Mapped[ReactionType] = mapped_column(
        Enum(ReactionType, name="reaction_type_enum", values_callable=lambda x: [e.value for e in x]),
        default=ReactionType.LIKE,
        nullable=False,
    )

    post = relationship("Post", back_populates="reactions")
    user = relationship("User")
