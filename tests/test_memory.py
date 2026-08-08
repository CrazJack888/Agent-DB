import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.memory_service import MemoryService
from src.core.models import MemoryCreate


@pytest.mark.asyncio
async def test_create_memory(mock_db):
    svc = MemoryService(mock_db)
    data = MemoryCreate(memory_type="working", content="hello")
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    with patch('src.services.memory_service.Memory', return_value=MagicMock()) as MockModel:
        result = await svc.create(data)
        assert MockModel.called


@pytest.mark.asyncio
async def test_list_memory(mock_db):
    svc = MemoryService(mock_db)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    items = await svc.list(agent_id="a1")
    assert items == []
