from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.email_log import EmailLog
from src.core.models import EmailLogCreate, EmailLogUpdate
import uuid


class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: EmailLogCreate) -> EmailLog:
        obj = EmailLog(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, email_id: uuid.UUID) -> Optional[EmailLog]:
        result = await self.db.execute(select(EmailLog).where(EmailLog.id == email_id))
        return result.scalar_one_or_none()

    async def list_by_customer(self, customer_id: uuid.UUID, direction: Optional[str] = None) -> List[EmailLog]:
        stmt = select(EmailLog).where(EmailLog.customer_id == customer_id)
        if direction:
            stmt = stmt.where(EmailLog.direction == direction)
        stmt = stmt.order_by(EmailLog.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_by_thread(self, thread_id: str) -> List[EmailLog]:
        stmt = select(EmailLog).where(EmailLog.thread_id == thread_id).order_by(EmailLog.created_at.asc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_pending(self, agent_id: Optional[str] = None) -> List[EmailLog]:
        stmt = select(EmailLog).where(EmailLog.status == "pending", EmailLog.direction == "inbound")
        if agent_id:
            stmt = stmt.where(EmailLog.agent_id == agent_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, email_id: uuid.UUID, data: EmailLogUpdate) -> Optional[EmailLog]:
        obj = await self.get(email_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, email_id: uuid.UUID) -> bool:
        obj = await self.get(email_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
