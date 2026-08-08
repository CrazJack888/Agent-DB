from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.memory import Memory
from src.core.models import MemoryCreate, MemoryUpdate, ContextItem
import uuid


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: MemoryCreate) -> Memory:
        obj = Memory(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, memory_id: uuid.UUID) -> Optional[Memory]:
        result = await self.db.execute(select(Memory).where(Memory.id == memory_id))
        return result.scalar_one_or_none()

    async def list(self, agent_id: Optional[str] = None, session_id: Optional[str] = None, memory_type: Optional[str] = None) -> List[Memory]:
        stmt = select(Memory)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if session_id:
            stmt = stmt.where(Memory.session_id == session_id)
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, memory_id: uuid.UUID, data: MemoryUpdate) -> Optional[Memory]:
        obj = await self.get(memory_id)
        if not obj:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, memory_id: uuid.UUID) -> bool:
        obj = await self.get(memory_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def search(self, query_embedding: Optional[List[float]] = None, agent_id: Optional[str] = None, session_id: Optional[str] = None, top_k: int = 5) -> List[ContextItem]:
        # Simplified vector search using L2 distance on ARRAY column if embedding provided
        stmt = select(Memory)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        if session_id:
            stmt = stmt.where(Memory.session_id == session_id)
        # If no embedding provided, fallback to recency
        if query_embedding:
            # Use a simple subquery with L2 distance approximation for pgvector-like behavior
            # Note: pure ARRAY does not have index; for production use pgvector extension properly
            stmt = stmt.order_by(func.coalesce(func.sqrt(
                func.sum([(Memory.embedding[i] - query_embedding[i]) * (Memory.embedding[i] - query_embedding[i]) for i in range(len(query_embedding))])
            ), 0).desc())
        else:
            stmt = stmt.order_by(Memory.created_at.desc())
        stmt = stmt.limit(top_k)
        result = await self.db.execute(stmt)
        items = []
        for row in result.scalars().all():
            items.append(ContextItem(source="memory", content=row.content, metadata={"type": row.memory_type, "agent_id": row.agent_id}))
        return items
