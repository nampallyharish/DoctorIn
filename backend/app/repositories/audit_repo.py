"""AuditLog Repository for recording all security and administrative events."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Data access for immutable audit logs."""

    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)

    async def log_action(
        self,
        action: str,
        resource_type: str,
        actor_id: uuid.UUID | None = None,
        resource_id: uuid.UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(log)
        await self.session.flush()
        return log
