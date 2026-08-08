from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.memory_service import MemoryService
from src.core.models import MemoryCreate, MemoryUpdate, MemoryOut
import uuid

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("", response_model=MemoryOut)
async def create_memory(data: MemoryCreate, db: AsyncSession = Depends(get_db)):
    svc = MemoryService(db)
    return await svc.create(data)


@router.get("/{memory_id}", response_model=MemoryOut)
async def get_memory(memory_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = MemoryService(db)
    obj = await svc.get(memory_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Memory not found")
    return obj


@router.get("", response_model=List[MemoryOut])
async def list_memory(agent_id: Optional[str] = None, session_id: Optional[str] = None, memory_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = MemoryService(db)
    return await svc.list(agent_id, session_id, memory_type)


@router.patch("/{memory_id}", response_model=MemoryOut)
async def update_memory(memory_id: uuid.UUID, data: MemoryUpdate, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    svc = MemoryService(db)
    obj = await svc.update(memory_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Memory not found")
    return obj


@router.delete("/{memory_id}")
async def delete_memory(memory_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    svc = MemoryService(db)
    ok = await svc.delete(memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"ok": True}
