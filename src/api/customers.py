from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.services.customer_service import CustomerService
from src.core.models import CustomerCreate, CustomerUpdate, CustomerOut
import uuid

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    # Check duplicate email
    existing = await svc.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Customer with this email already exists")
    return await svc.create(data)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    obj = await svc.get(customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


@router.get("", response_model=List[CustomerOut])
async def list_customers(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    return await svc.list(status)


@router.get("/by-email/{email}", response_model=CustomerOut)
async def get_customer_by_email(email: str, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    obj = await svc.get_by_email(email)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: uuid.UUID, data: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    obj = await svc.update(customer_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


@router.delete("/{customer_id}")
async def delete_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = CustomerService(db)
    ok = await svc.delete(customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"ok": True}
