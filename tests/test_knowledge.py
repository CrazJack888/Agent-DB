import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.knowledge_service import KnowledgeService
from src.core.models import KnowledgeCreate


@pytest.mark.asyncio
async def test_create_knowledge(mock_db):
    svc = KnowledgeService(mock_db)
    data = KnowledgeCreate(doc_id="d1", chunk_content="test chunk")
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    with patch('src.services.knowledge_service.Knowledge', return_value=MagicMock()) as MockModel:
        result = await svc.create(data)
        assert MockModel.called


@pytest.mark.asyncio
async def test_search_knowledge(mock_db):
    svc = KnowledgeService(mock_db)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    items = await svc.search(top_k=3)
    assert items == []
