from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.state_service import StateService
from src.core.models import StateCreate, StateUpdate, StateOut
import uuid

router = APIRouter(prefix="/state", tags=["state"])


@router.post("", response_model=StateOut)
async def create_state(data: StateCreate, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    return await svc.create(data)


@router.get("/{state_id}", response_model=StateOut)
async def get_state(state_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    obj = await svc.get(state_id)
    if not obj:
        raise HTTPException(status_code=404, detail="State not found")
    return obj


@router.get("/session/{session_id}", response_model=StateOut)
async def get_state_by_session(session_id: str, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    obj = await svc.get_by_session(session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="State not found")
    return obj


@router.get("", response_model=List[StateOut])
async def list_state(agent_id: Optional[str] = None, session_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    return await svc.list(agent_id, session_id)


@router.patch("/{state_id}", response_model=StateOut)
async def update_state(state_id: uuid.UUID, data: StateUpdate, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    obj = await svc.update(state_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="State not found")
    return obj


@router.delete("/{state_id}")
async def delete_state(state_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = StateService(db)
    ok = await svc.delete(state_id)
    if not ok:
        raise HTTPException(status_code=404, detail="State not found")
    return {"ok": True}
