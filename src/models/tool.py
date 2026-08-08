import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    api_schema: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    function_schema: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    permission_rules: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
