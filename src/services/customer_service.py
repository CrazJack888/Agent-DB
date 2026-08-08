from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.customer import Customer
from src.core.models import CustomerCreate, CustomerUpdate
import uuid


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CustomerCreate) -> Customer:
        obj = Customer(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, customer_id: uuid.UUID) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.email == email))
        return result.scalar_one_or_none()

    async def list(self, status: Optional[str] = None) -> List[Customer]:
        stmt = select(Customer)
        if status:
            stmt = stmt.where(Customer.status == status)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, customer_id: uuid.UUID, data: CustomerUpdate) -> Optional[Customer]:
        obj = await self.get(customer_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, customer_id: uuid.UUID) -> bool:
        obj = await self.get(customer_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
