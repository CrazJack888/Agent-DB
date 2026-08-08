from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.email_service import EmailService
from src.core.models import EmailLogCreate, EmailLogUpdate, EmailLogOut
import uuid

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/inbound", response_model=EmailLogOut)
async def create_inbound_email(data: EmailLogCreate, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    return await svc.create(data)


@router.post("/outbound", response_model=EmailLogOut)
async def create_outbound_email(data: EmailLogCreate, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    return await svc.create(data)


@router.get("/{email_id}", response_model=EmailLogOut)
async def get_email(email_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    obj = await svc.get(email_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Email not found")
    return obj


@router.get("", response_model=List[EmailLogOut])
async def list_emails(customer_id: Optional[uuid.UUID] = None, direction: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    if customer_id:
        return await svc.list_by_customer(customer_id, direction)
    # Fallback: list all (not ideal for large datasets, but kept simple)
    from sqlalchemy import select
    from src.models.email_log import EmailLog
    stmt = select(EmailLog)
    if direction:
        stmt = stmt.where(EmailLog.direction == direction)
    stmt = stmt.order_by(EmailLog.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/thread/{thread_id}", response_model=List[EmailLogOut])
async def list_emails_by_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    return await svc.list_by_thread(thread_id)


@router.get("/pending/list", response_model=List[EmailLogOut])
async def list_pending_emails(agent_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    return await svc.list_pending(agent_id)


@router.patch("/{email_id}", response_model=EmailLogOut)
async def update_email(email_id: uuid.UUID, data: EmailLogUpdate, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    obj = await svc.update(email_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Email not found")
    return obj


@router.delete("/{email_id}")
async def delete_email(email_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = EmailService(db)
    ok = await svc.delete(email_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"ok": True}
