import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.execute = AsyncMock()
    db.scalars = MagicMock()
    db.scalar_one_or_none = AsyncMock()
    return db
