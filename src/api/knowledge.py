from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.knowledge_service import KnowledgeService
from src.core.models import KnowledgeCreate, KnowledgeUpdate, KnowledgeOut
import uuid

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("", response_model=KnowledgeOut)
async def create_knowledge(data: KnowledgeCreate, db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    return await svc.create(data)


@router.get("/{knowledge_id}", response_model=KnowledgeOut)
async def get_knowledge(knowledge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    obj = await svc.get(knowledge_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return obj


@router.get("", response_model=List[KnowledgeOut])
async def list_knowledge(doc_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    return await svc.list(doc_id)


@router.patch("/{knowledge_id}", response_model=KnowledgeOut)
async def update_knowledge(knowledge_id: uuid.UUID, data: KnowledgeUpdate, db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    obj = await svc.update(knowledge_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return obj


@router.delete("/{knowledge_id}")
async def delete_knowledge(knowledge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    ok = await svc.delete(knowledge_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return {"ok": True}
