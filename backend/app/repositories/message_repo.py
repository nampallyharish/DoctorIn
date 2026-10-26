"""Messaging Repository for conversation membership, message persistence, and privacy checks."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.doctor import Doctor
from app.models.message import (
    Conversation,
    ConversationMember,
    ConversationType,
    Message,
    MessageType,
)
from app.models.user import User
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Data access repository for private conversations and messages."""

    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def is_user_member_of_conversation(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Security check: Verify that user is a member of the requested conversation."""
        query = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id,
            ConversationMember.left_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def find_existing_1on1_conversation(
        self, user1_id: uuid.UUID, user2_id: uuid.UUID
    ) -> Conversation | None:
        """Check if a direct conversation already exists between two users."""
        # Find conversation IDs where both users are members
        query = (
            select(ConversationMember.conversation_id)
            .where(
                or_(
                    ConversationMember.user_id == user1_id,
                    ConversationMember.user_id == user2_id,
                )
            )
            .group_by(ConversationMember.conversation_id)
            .having(func.count(ConversationMember.user_id) == 2)
        )
        result = await self.session.execute(query)
        conv_id = result.scalar_one_or_none()
        if conv_id:
            return await self.session.get(Conversation, conv_id)
        return None

    async def create_1on1_conversation(
        self,
        sender_user_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        conv_type: ConversationType = ConversationType.DOCTOR_TO_DOCTOR,
    ) -> Conversation:
        """Create a new 1-on-1 private conversation with two members."""
        now = datetime.now(timezone.utc)
        conv = Conversation(
            conversation_type=conv_type,
            last_message_at=now,
        )
        self.session.add(conv)
        await self.session.flush()

        member1 = ConversationMember(
            conversation_id=conv.id,
            user_id=sender_user_id,
            joined_at=now,
        )
        member2 = ConversationMember(
            conversation_id=conv.id,
            user_id=recipient_user_id,
            joined_at=now,
        )
        self.session.add(member1)
        self.session.add(member2)
        await self.session.flush()

        return conv

    async def list_user_conversations(
        self, user_id: uuid.UUID
    ) -> list[tuple[Conversation, ConversationMember, Doctor, Message | None, int]]:
        """
        List all active conversations for a user with the other participant details,
        last message, and unread message count.
        """
        # 1. Fetch user's conversation memberships
        query = (
            select(ConversationMember)
            .where(
                ConversationMember.user_id == user_id,
                ConversationMember.left_at.is_(None),
            )
            .options(
                selectinload(ConversationMember.conversation).selectinload(
                    Conversation.members
                ).selectinload(ConversationMember.user).selectinload(User.doctor_profile),
            )
            .order_by(desc(ConversationMember.conversation_id))
        )
        result = await self.session.execute(query)
        memberships = result.scalars().all()

        results = []
        for m in memberships:
            conv = m.conversation
            # Find the other participant
            other_member = next((om for om in conv.members if om.user_id != user_id), None)
            if not other_member or not other_member.user or not other_member.user.doctor_profile:
                continue

            other_doctor = other_member.user.doctor_profile

            # Fetch last message
            last_msg_q = (
                select(Message)
                .where(Message.conversation_id == conv.id, Message.deleted_at.is_(None))
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            last_msg_res = await self.session.execute(last_msg_q)
            last_message = last_msg_res.scalar_one_or_none()

            # Calculate unread count (messages created after user's last_read_at)
            unread_count = 0
            if m.last_read_at:
                unread_q = select(func.count(Message.id)).where(
                    Message.conversation_id == conv.id,
                    Message.sender_id != user_id,
                    Message.created_at > m.last_read_at,
                    Message.deleted_at.is_(None),
                )
                unread_count = await self.session.scalar(unread_q) or 0

            results.append((conv, m, other_doctor, last_message, unread_count))

        # Sort by last_message_at desc
        results.sort(
            key=lambda x: x[0].last_message_at if x[0].last_message_at else datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return results

    async def list_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 50,
    ) -> list[Message]:
        """Fetch messages in chronological order for conversation."""
        query = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None),
            )
            .options(
                selectinload(Message.sender).selectinload(User.doctor_profile),
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def send_message(
        self,
        conversation_id: uuid.UUID,
        sender_id: uuid.UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
    ) -> Message:
        """Create and store message, updating conversation last_message_at timestamp."""
        now = datetime.now(timezone.utc)
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
        )
        self.session.add(message)

        # Update conversation last_message_at
        conv_stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(last_message_at=now)
        )
        await self.session.execute(conv_stmt)

        # Update sender's last_read_at
        member_stmt = (
            update(ConversationMember)
            .where(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == sender_id,
            )
            .values(last_read_at=now)
        )
        await self.session.execute(member_stmt)
        await self.session.flush()

        return message

    async def mark_conversation_as_read(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Update last_read_at timestamp for a conversation member."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(ConversationMember)
            .where(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == user_id,
            )
            .values(last_read_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()
