from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.state import State
from src.core.models import StateCreate, StateUpdate
import uuid


class StateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: StateCreate) -> State:
        obj = State(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, state_id: uuid.UUID) -> Optional[State]:
        result = await self.db.execute(select(State).where(State.id == state_id))
        return result.scalar_one_or_none()

    async def get_by_session(self, session_id: str) -> Optional[State]:
        result = await self.db.execute(select(State).where(State.session_id == session_id).order_by(State.created_at.desc()))
        return result.scalars().first()

    async def list(self, agent_id: Optional[str] = None, session_id: Optional[str] = None) -> List[State]:
        stmt = select(State)
        if agent_id:
            stmt = stmt.where(State.agent_id == agent_id)
        if session_id:
            stmt = stmt.where(State.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, state_id: uuid.UUID, data: StateUpdate) -> Optional[State]:
        obj = await self.get(state_id)
        if not obj:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, state_id: uuid.UUID) -> bool:
        obj = await self.get(state_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
