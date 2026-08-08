from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.core.gateway import AgentGateway
from src.core.models import BuildContextRequest, Context

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/context", response_model=Context)
async def build_context(req: BuildContextRequest, db: AsyncSession = Depends(get_db)):
    gateway = AgentGateway(db)
    return await gateway.build_context(req.query, req.agent_id, req.session_id, req.top_k)


@router.get("/workflow/{name}")
async def get_workflow(name: str, db: AsyncSession = Depends(get_db)):
    gateway = AgentGateway(db)
    wf = await gateway.get_workflow(name)
    if not wf:
        return {"detail": "Workflow not found"}
    return wf
