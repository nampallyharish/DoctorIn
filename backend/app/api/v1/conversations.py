"""Doctor-to-Doctor Messaging REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.message import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.messaging_service import MessagingService

router = APIRouter(prefix="/conversations", tags=["Doctor-to-Doctor Messaging"])


@router.get(
    "",
    response_model=APIResponse[list[ConversationResponse]],
    summary="List all active doctor-to-doctor conversations",
)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List private messaging threads with other verified doctors."""
    service = MessagingService(db)
    conversations = await service.list_conversations(current_user)
    return APIResponse(success=True, data=conversations)


@router.post(
    "",
    response_model=APIResponse[ConversationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Initiate or resume conversation with another verified doctor",
)
async def start_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a private message thread.
    Enforces that BOTH sender and recipient are DoctorIn Verified doctors.
    """
    service = MessagingService(db)
    conv = await service.get_or_create_conversation(current_user, payload)
    return APIResponse(success=True, data=conv)


@router.get(
    "/{conversation_id}/messages",
    response_model=APIResponse[list[MessageResponse]],
    summary="Fetch message history for conversation",
)
async def list_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch message timeline.
    Enforces that requesting doctor is an active member of this conversation.
    """
    service = MessagingService(db)
    messages = await service.list_messages(current_user, conversation_id)
    return APIResponse(success=True, data=messages)


@router.post(
    "/{conversation_id}/messages",
    response_model=APIResponse[MessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in conversation",
)
async def send_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send text message to peer doctor."""
    service = MessagingService(db)
    message = await service.send_message(current_user, conversation_id, payload)
    return APIResponse(success=True, data=message)
