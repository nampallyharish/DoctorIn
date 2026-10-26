"""Messaging and conversation database models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, SoftDeleteMixin


class ConversationType(str, enum.Enum):
    DOCTOR_TO_DOCTOR = "doctor_to_doctor"
    HOSPITAL_TO_DOCTOR = "hospital_to_doctor"


class ConversationMemberRole(str, enum.Enum):
    PARTICIPANT = "participant"
    ADMIN = "admin"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class Conversation(BaseModel):
    __tablename__ = "conversations"

    conversation_type: Mapped[ConversationType] = mapped_column(
        Enum(ConversationType, name="conversation_type_enum", values_callable=lambda x: [e.value for e in x]),
        default=ConversationType.DOCTOR_TO_DOCTOR,
        nullable=False,
    )
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    members = relationship("ConversationMember", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class ConversationMember(BaseModel):
    __tablename__ = "conversation_members"
    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", name="uq_conversation_member"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ConversationMemberRole] = mapped_column(
        Enum(ConversationMemberRole, name="conversation_member_role_enum", values_callable=lambda x: [e.value for e in x]),
        default=ConversationMemberRole.PARTICIPANT,
        nullable=False,
    )
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", back_populates="members")
    user = relationship("User")


class Message(BaseModel, SoftDeleteMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type_enum", values_callable=lambda x: [e.value for e in x]),
        default=MessageType.TEXT,
        nullable=False,
    )
    media_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")
