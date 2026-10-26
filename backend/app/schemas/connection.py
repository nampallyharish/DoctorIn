"""Connection schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.doctor import ConnectionStatus


class ConnectionRequestCreate(BaseModel):
    recipient_doctor_id: uuid.UUID


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    requester_id: uuid.UUID
    recipient_id: uuid.UUID
    status: ConnectionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConnectionAction(BaseModel):
    action: str  # "accept", "reject", "block"
