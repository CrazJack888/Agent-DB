from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.tool import Tool
from src.core.models import ToolCreate, ToolUpdate
import uuid


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ToolCreate) -> Tool:
        obj = Tool(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, tool_id: uuid.UUID) -> Optional[Tool]:
        result = await self.db.execute(select(Tool).where(Tool.id == tool_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Tool]:
        result = await self.db.execute(select(Tool).where(Tool.name == name))
        return result.scalar_one_or_none()

    async def list(self) -> List[Tool]:
        result = await self.db.execute(select(Tool))
        return result.scalars().all()

    async def update(self, tool_id: uuid.UUID, data: ToolUpdate) -> Optional[Tool]:
        obj = await self.get(tool_id)
        if not obj:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, tool_id: uuid.UUID) -> bool:
        obj = await self.get(tool_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
