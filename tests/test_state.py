import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.state_service import StateService
from src.core.models import StateCreate


@pytest.mark.asyncio
async def test_create_state(mock_db):
    svc = StateService(mock_db)
    data = StateCreate(session_id="s1", task_status="running")
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    with patch('src.services.state_service.State', return_value=MagicMock()) as MockModel:
        result = await svc.create(data)
        assert MockModel.called


@pytest.mark.asyncio
async def test_get_state_by_session(mock_db):
    svc = StateService(mock_db)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await svc.get_by_session("s1")
    assert result is None
