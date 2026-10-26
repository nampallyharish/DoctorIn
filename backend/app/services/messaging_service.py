"""Messaging Service enforcing strict verified doctor-to-doctor communication rules."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logging import logger
from app.models.doctor import Doctor, VerificationStatus
from app.models.message import ConversationType
from app.models.user import User, UserRole
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.message import (
    ConversationCreate,
    ConversationResponse,
    LastMessageSummary,
    MessageCreate,
    MessageResponse,
    ParticipantSummary,
)


class MessagingService:
    """Coordinates verified doctor-to-doctor messaging and enforces authorization guardrails."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.msg_repo = MessageRepository(db)
        self.doc_repo = DoctorRepository(db)

    async def _validate_verified_doctor(self, user: User) -> Doctor:
        """Enforces Rule 1 & 2: Caller must be a verified doctor."""
        if user.role != UserRole.DOCTOR:
            raise ForbiddenError("Direct messaging is restricted to verified medical doctors.")

        doc = await self.doc_repo.get_by_user_id(user.id)
        if not doc:
            raise NotFoundError("Doctor profile not found.")

        if doc.verification_status != VerificationStatus.VERIFIED:
            raise ForbiddenError(
                "Access restricted: Professional messaging requires an approved DoctorIn Verified badge."
            )

        return doc

    async def get_or_create_conversation(
        self, user: User, payload: ConversationCreate
    ) -> ConversationResponse:
        """
        Start or resume a 1-on-1 conversation with another doctor.
        Enforces Rule 3: BOTH participants must be DoctorIn Verified.
        """
        sender_doctor = await self._validate_verified_doctor(user)

        # Cannot message oneself
        if sender_doctor.id == payload.recipient_doctor_id:
            raise ValidationError("You cannot initiate a conversation with yourself.")

        # Validate recipient doctor
        recipient_doctor = await self.doc_repo.get_by_id(payload.recipient_doctor_id)
        if not recipient_doctor:
            raise NotFoundError("Recipient doctor not found.")

        if recipient_doctor.verification_status != VerificationStatus.VERIFIED:
            raise ForbiddenError(
                "Cannot initiate conversation: The recipient doctor has not yet verified their medical credentials."
            )

        # Check if conversation already exists
        conv = await self.msg_repo.find_existing_1on1_conversation(
            sender_doctor.user_id, recipient_doctor.user_id
        )

        if not conv:
            conv = await self.msg_repo.create_1on1_conversation(
                sender_user_id=sender_doctor.user_id,
                recipient_user_id=recipient_doctor.user_id,
                conv_type=ConversationType.DOCTOR_TO_DOCTOR,
            )
            logger.info(
                f"💬 Conversation {conv.id} created between verified doctors {sender_doctor.id} and {recipient_doctor.id}"
            )

        return ConversationResponse(
            id=conv.id,
            conversation_type=conv.conversation_type,
            last_message_at=conv.last_message_at,
            participant=ParticipantSummary(
                doctor_id=recipient_doctor.id,
                user_id=recipient_doctor.user_id,
                full_name=recipient_doctor.full_name,
                slug=recipient_doctor.slug,
                headline=recipient_doctor.headline,
                profile_photo_key=recipient_doctor.profile_photo_key,
                verification_status=recipient_doctor.verification_status.value,
            ),
            last_message=None,
            unread_count=0,
        )

    async def list_conversations(self, user: User) -> list[ConversationResponse]:
        """List active conversations for verified doctor."""
        await self._validate_verified_doctor(user)

        items = await self.msg_repo.list_user_conversations(user.id)
        out = []
        for conv, member, other_doc, last_msg, unread_count in items:
            last_msg_summary = None
            if last_msg:
                last_msg_summary = LastMessageSummary(
                    content=last_msg.content,
                    sender_id=last_msg.sender_id,
                    created_at=last_msg.created_at,
                )

            out.append(
                ConversationResponse(
                    id=conv.id,
                    conversation_type=conv.conversation_type,
                    last_message_at=conv.last_message_at,
                    participant=ParticipantSummary(
                        doctor_id=other_doc.id,
                        user_id=other_doc.user_id,
                        full_name=other_doc.full_name,
                        slug=other_doc.slug,
                        headline=other_doc.headline,
                        profile_photo_key=other_doc.profile_photo_key,
                        verification_status=other_doc.verification_status.value,
                    ),
                    last_message=last_msg_summary,
                    unread_count=unread_count,
                )
            )
        return out

    async def list_messages(
        self, user: User, conversation_id: uuid.UUID
    ) -> list[MessageResponse]:
        """Fetch message history. Enforces conversation membership privacy check."""
        await self._validate_verified_doctor(user)

        # Enforce membership check
        is_member = await self.msg_repo.is_user_member_of_conversation(conversation_id, user.id)
        if not is_member:
            raise ForbiddenError("Access denied: You are not a participant in this conversation.")

        # Mark conversation as read
        await self.msg_repo.mark_conversation_as_read(conversation_id, user.id)

        messages = await self.msg_repo.list_messages(conversation_id)
        out = []
        for m in messages:
            doc = m.sender.doctor_profile if m.sender else None
            sender_name = doc.full_name if doc else "Doctor"
            sender_avatar = doc.profile_photo_key if doc else None

            out.append(
                MessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    sender_id=m.sender_id,
                    sender_name=sender_name,
                    sender_avatar_key=sender_avatar,
                    is_self=m.sender_id == user.id,
                    content=m.content,
                    message_type=m.message_type,
                    is_edited=m.is_edited,
                    created_at=m.created_at,
                )
            )
        return out

    async def send_message(
        self, user: User, conversation_id: uuid.UUID, payload: MessageCreate
    ) -> MessageResponse:
        """Send message in conversation."""
        sender_doctor = await self._validate_verified_doctor(user)

        is_member = await self.msg_repo.is_user_member_of_conversation(conversation_id, user.id)
        if not is_member:
            raise ForbiddenError("Access denied: You are not a participant in this conversation.")

        msg = await self.msg_repo.send_message(
            conversation_id=conversation_id,
            sender_id=user.id,
            content=payload.content,
            message_type=payload.message_type,
        )

        return MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=user.id,
            sender_name=sender_doctor.full_name,
            sender_avatar_key=sender_doctor.profile_photo_key,
            is_self=True,
            content=msg.content,
            message_type=msg.message_type,
            is_edited=False,
            created_at=msg.created_at,
        )
