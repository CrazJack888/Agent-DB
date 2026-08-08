import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.tool_service import ToolService
from src.core.models import ToolCreate


@pytest.mark.asyncio
async def test_create_tool(mock_db):
    svc = ToolService(mock_db)
    data = ToolCreate(name="search_knowledge")
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    with patch('src.services.tool_service.Tool', return_value=MagicMock()) as MockModel:
        result = await svc.create(data)
        assert MockModel.called
