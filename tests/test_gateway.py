import pytest
from unittest.mock import patch, AsyncMock
from src.core.gateway import AgentGateway
from src.core.models import Context


@pytest.mark.asyncio
async def test_build_context(mock_db):
    gateway = AgentGateway(mock_db)
    
    with patch.object(gateway.memory, 'search', new_callable=AsyncMock) as mock_mem, \
         patch.object(gateway.knowledge, 'search', new_callable=AsyncMock) as mock_know, \
         patch.object(gateway.workflow, 'get_by_name', new_callable=AsyncMock) as mock_wf:
        
        mock_mem.return_value = []
        mock_know.return_value = []
        mock_wf.return_value = None
        
        ctx = await gateway.build_context("test query", agent_id="a1", session_id="s1")
        assert isinstance(ctx, Context)
        assert ctx.query == "test query"
        assert ctx.items == []
