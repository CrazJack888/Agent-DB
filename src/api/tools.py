from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.tool_service import ToolService
from src.services.customer_service import CustomerService
from src.services.email_service import EmailService
from src.core.models import ToolCreate, ToolUpdate, ToolOut, SendEmailRequest, SendEmailResponse
import uuid

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("", response_model=ToolOut)
async def create_tool(data: ToolCreate, db: AsyncSession = Depends(get_db)):
    svc = ToolService(db)
    return await svc.create(data)


@router.get("/{tool_id}", response_model=ToolOut)
async def get_tool(tool_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = ToolService(db)
    obj = await svc.get(tool_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tool not found")
    return obj


@router.get("", response_model=List[ToolOut])
async def list_tools(db: AsyncSession = Depends(get_db)):
    svc = ToolService(db)
    return await svc.list()


@router.patch("/{tool_id}", response_model=ToolOut)
async def update_tool(tool_id: uuid.UUID, data: ToolUpdate, db: AsyncSession = Depends(get_db)):
    svc = ToolService(db)
    obj = await svc.update(tool_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Tool not found")
    return obj


@router.delete("/{tool_id}")
async def delete_tool(tool_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = ToolService(db)
    ok = await svc.delete(tool_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"ok": True}


@router.post("/send_email/execute", response_model=SendEmailResponse)
async def execute_send_email(req: SendEmailRequest, db: AsyncSession = Depends(get_db)):
    """
    Execute the send_email tool.
    In a production system this would connect to SMTP or an email API.
    For demo purposes, it records the email in EmailLog as outbound.
    """
    customer_svc = CustomerService(db)
    email_svc = EmailService(db)

    customer = await customer_svc.get_by_email(req.to)
    if not customer:
        return SendEmailResponse(success=False, message=f"Customer with email {req.to} not found")

    email_data = EmailLogCreate(
        customer_id=customer.id,
        direction="outbound",
        subject=req.subject,
        content=req.body,
        status="sent",
        thread_id=req.thread_id,
        metadata_json={"simulated": True, "note": "In production this would call SMTP"},
    )
    email_record = await email_svc.create(email_data)

    return SendEmailResponse(
        success=True,
        message="Email sent and logged successfully (simulated)",
        email_id=email_record.id,
    )
