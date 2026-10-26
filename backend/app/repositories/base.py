"""Generic Base Repository providing standard async CRUD operations."""

import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD Repository pattern implementation."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Fetch single record by its UUID primary key."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> Sequence[ModelType]:
        """Fetch multiple records with offset pagination and optional filters."""
        query = select(self.model).offset(skip).limit(limit)
        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr):
                    query = query.where(getattr(self.model, attr) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self, filters: dict | None = None) -> int:
        """Count total matching records."""
        query = select(func.count()).select_from(self.model)
        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr):
                    query = query.where(getattr(self.model, attr) == value)
        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def create(self, **kwargs: Any) -> ModelType:
        """Create and persist a new model instance."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, **kwargs: Any) -> ModelType | None:
        """Update fields of an existing model instance."""
        instance = await self.get_by_id(id)
        if instance:
            for attr, value in kwargs.items():
                if hasattr(instance, attr):
                    setattr(instance, attr, value)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID) -> bool:
        """Hard delete a record by ID."""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False
