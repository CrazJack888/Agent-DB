from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.workflow_service import WorkflowService
from src.core.models import WorkflowCreate, WorkflowUpdate, WorkflowOut
import uuid

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowOut)
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    svc = WorkflowService(db)
    return await svc.create(data)


@router.get("/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = WorkflowService(db)
    obj = await svc.get(workflow_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return obj


@router.get("", response_model=List[WorkflowOut])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    svc = WorkflowService(db)
    return await svc.list()


@router.patch("/{workflow_id}", response_model=WorkflowOut)
async def update_workflow(workflow_id: uuid.UUID, data: WorkflowUpdate, db: AsyncSession = Depends(get_db)):
    svc = WorkflowService(db)
    obj = await svc.update(workflow_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return obj


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = WorkflowService(db)
    ok = await svc.delete(workflow_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"ok": True}
