from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.knowledge import Knowledge
from src.core.models import KnowledgeCreate, KnowledgeUpdate, ContextItem
import uuid


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: KnowledgeCreate) -> Knowledge:
        obj = Knowledge(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, knowledge_id: uuid.UUID) -> Optional[Knowledge]:
        result = await self.db.execute(select(Knowledge).where(Knowledge.id == knowledge_id))
        return result.scalar_one_or_none()

    async def list(self, doc_id: Optional[str] = None) -> List[Knowledge]:
        stmt = select(Knowledge)
        if doc_id:
            stmt = stmt.where(Knowledge.doc_id == doc_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, knowledge_id: uuid.UUID, data: KnowledgeUpdate) -> Optional[Knowledge]:
        obj = await self.get(knowledge_id)
        if not obj:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, knowledge_id: uuid.UUID) -> bool:
        obj = await self.get(knowledge_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def search(self, query_embedding: Optional[List[float]] = None, top_k: int = 5) -> List[ContextItem]:
        stmt = select(Knowledge).order_by(Knowledge.created_at.desc()).limit(top_k)
        result = await self.db.execute(stmt)
        items = []
        for row in result.scalars().all():
            items.append(ContextItem(source="knowledge", content=row.chunk_content, metadata={"doc_id": row.doc_id}))
        return items
