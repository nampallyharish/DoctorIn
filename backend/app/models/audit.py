"""AuditLog, Report, and City models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

JSONType = JSON().with_variant(JSONB, "postgresql")


class TargetType(str, enum.Enum):
    POST = "post"
    COMMENT = "comment"
    USER = "user"
    MESSAGE = "message"
    HOSPITAL = "hospital"


class ReportReason(str, enum.Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    INAPPROPRIATE = "inappropriate"
    FAKE_CREDENTIALS = "fake_credentials"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class City(BaseModel):
    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    state: Mapped[str | None] = mapped_column(String(200), nullable=True)
    country: Mapped[str] = mapped_column(String(3), default="IND", nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Report(BaseModel):
    __tablename__ = "reports"

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_type: Mapped[TargetType] = mapped_column(
        Enum(TargetType, name="target_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    reason: Mapped[ReportReason] = mapped_column(
        Enum(ReportReason, name="report_reason_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=ReportStatus.PENDING,
        nullable=False,
        index=True,
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_id])
    admin = relationship("User", foreign_keys=[admin_id])


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    actor = relationship("User")
