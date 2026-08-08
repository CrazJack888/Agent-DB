from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.context_engine import ContextEngine
from src.core.models import Context, ContextItem
from src.services.memory_service import MemoryService
from src.services.knowledge_service import KnowledgeService
from src.services.workflow_service import WorkflowService
from src.services.state_service import StateService


class AgentGateway:
    def __init__(self, db: AsyncSession):
        self.memory = MemoryService(db)
        self.knowledge = KnowledgeService(db)
        self.workflow = WorkflowService(db)
        self.state = StateService(db)
        self.context_engine = ContextEngine()

    async def build_context(self, query: str, agent_id: Optional[str] = None, session_id: Optional[str] = None, top_k: int = 5) -> Context:
        # Retrieve from multiple sources
        memory_items = await self.memory.search(agent_id=agent_id, session_id=session_id, top_k=top_k)
        knowledge_items = await self.knowledge.search(top_k=top_k)
        # Graph expansion simplified: treat workflow relations as graph-like context
        graph_items: List[ContextItem] = []
        wf = await self.workflow.get_by_name("analysis")
        if wf:
            graph_items.append(ContextItem(source="graph", content=str(wf.task_graph), metadata={"workflow": wf.name}))
        context = self.context_engine.build(query, memory_items, knowledge_items, graph_items)
        # Gateway acts as gatekeeper: enforce top_k limit on final merged context
        context.items = context.items[:top_k]
        return context

    async def get_workflow(self, name: str):
        return await self.workflow.get_by_name(name)
