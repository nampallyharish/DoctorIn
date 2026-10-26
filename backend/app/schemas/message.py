"""Pydantic schemas for Doctor-to-Doctor Messaging and Conversations."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.message import ConversationType, MessageType


class ConversationCreate(BaseModel):
    recipient_doctor_id: uuid.UUID = Field(
        ..., description="UUID of the recipient doctor (must also be DoctorIn Verified)"
    )


class ParticipantSummary(BaseModel):
    doctor_id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    slug: str
    headline: str | None = None
    profile_photo_key: str | None = None
    verification_status: str


class LastMessageSummary(BaseModel):
    content: str
    sender_id: uuid.UUID
    created_at: datetime


class ConversationResponse(BaseModel):
    id: uuid.UUID
    conversation_type: ConversationType
    last_message_at: datetime | None = None
    participant: ParticipantSummary
    last_message: LastMessageSummary | None = None
    unread_count: int = 0


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Message text content")
    message_type: MessageType = MessageType.TEXT


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    sender_name: str
    sender_avatar_key: str | None = None
    is_self: bool
    content: str
    message_type: MessageType
    is_edited: bool
    created_at: datetime
