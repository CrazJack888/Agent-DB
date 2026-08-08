from fastapi import APIRouter
from src.api import gateway, memory, workflow, knowledge, tools, state, customers, emails

api_router = APIRouter()
api_router.include_router(gateway.router)
api_router.include_router(memory.router)
api_router.include_router(workflow.router)
api_router.include_router(knowledge.router)
api_router.include_router(tools.router)
api_router.include_router(state.router)
api_router.include_router(customers.router)
api_router.include_router(emails.router)
