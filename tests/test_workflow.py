import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.workflow_service import WorkflowService
from src.core.models import WorkflowCreate


@pytest.mark.asyncio
async def test_create_workflow(mock_db):
    svc = WorkflowService(mock_db)
    data = WorkflowCreate(name="analysis", task_graph={"steps": []})
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    with patch('src.services.workflow_service.Workflow', return_value=MagicMock()) as MockModel:
        result = await svc.create(data)
        assert MockModel.called


@pytest.mark.asyncio
async def test_get_workflow_by_name(mock_db):
    svc = WorkflowService(mock_db)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await svc.get_by_name("analysis")
    assert result is None
