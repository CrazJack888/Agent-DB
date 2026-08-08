from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.workflow import Workflow
from src.core.models import WorkflowCreate, WorkflowUpdate
import uuid


class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: WorkflowCreate) -> Workflow:
        obj = Workflow(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Workflow]:
        result = await self.db.execute(select(Workflow).where(Workflow.name == name))
        return result.scalar_one_or_none()

    async def list(self) -> List[Workflow]:
        result = await self.db.execute(select(Workflow))
        return result.scalars().all()

    async def update(self, workflow_id: uuid.UUID, data: WorkflowUpdate) -> Optional[Workflow]:
        obj = await self.get(workflow_id)
        if not obj:
            return None
        for k, v in data.dict(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, workflow_id: uuid.UUID) -> bool:
        obj = await self.get(workflow_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
