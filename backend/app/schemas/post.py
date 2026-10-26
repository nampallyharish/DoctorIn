"""Pydantic schemas for Social Feed Posts, Media, Comments, Reactions, and Moderation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.post import (
    AuthorType,
    MediaType,
    PostType,
    PostVisibility,
    ReactionType,
)


class PostMediaItem(BaseModel):
    id: uuid.UUID
    media_key: str
    media_type: MediaType
    original_name: str | None = None
    url: str | None = None


class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Post text content")
    post_type: PostType = PostType.TEXT
    visibility: PostVisibility = PostVisibility.PUBLIC
    media_keys: list[str] | None = Field(default=[], description="Uploaded S3 keys for images/documents")


class PostUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=10000)
    visibility: PostVisibility | None = None


class PostCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_comment_id: uuid.UUID | None = None


class PostCommentResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    author_headline: str | None = None
    author_verified: bool = False
    content: str
    parent_comment_id: uuid.UUID | None = None
    created_at: datetime


class PostReactionCreate(BaseModel):
    reaction_type: ReactionType = ReactionType.LIKE


class PostResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_type: AuthorType
    author_name: str
    author_slug: str | None = None
    author_headline: str | None = None
    author_avatar_key: str | None = None
    author_verified: bool = False
    content: str
    post_type: PostType
    visibility: PostVisibility
    reaction_count: int
    comment_count: int
    user_reaction: str | None = None
    is_pinned: bool = False
    media: list[PostMediaItem] = []
    created_at: datetime
    updated_at: datetime


class PostReportCreate(BaseModel):
    reason: str = Field(..., pattern="^(spam|harassment|misinformation|inappropriate|fake_credentials|other)$")
    description: str | None = Field(None, max_length=1000)
