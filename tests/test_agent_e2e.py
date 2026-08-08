"""
End-to-end test for the Agent core workflow.

Tests the full path: Agent query -> Gateway -> Services -> ContextEngine -> structured Context.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.gateway import AgentGateway
from src.core.models import ContextItem, Context, BuildContextRequest
from src.models.memory import Memory
from src.models.knowledge import Knowledge
from src.models.workflow import Workflow


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def fake_memory_rows():
    """Simulate Memory ORM rows returned from DB."""
    m1 = MagicMock(spec=Memory)
    m1.content = "User prefers concise answers."
    m1.memory_type = "semantic"
    m1.agent_id = "agent_001"
    m1.session_id = "session_abc"
    m1.embedding = None

    m2 = MagicMock(spec=Memory)
    m2.content = "Previous task: summarize report."
    m2.memory_type = "episodic"
    m2.agent_id = "agent_001"
    m2.session_id = "session_abc"
    m2.embedding = None
    return [m1, m2]


@pytest.fixture
def fake_knowledge_rows():
    """Simulate Knowledge ORM rows returned from DB."""
    k1 = MagicMock(spec=Knowledge)
    k1.chunk_content = "Q3 revenue increased by 15%."
    k1.doc_id = "report_q3"
    k1.embedding = None

    k2 = MagicMock(spec=Knowledge)
    k2.chunk_content = "New product line launched in Asia."
    k2.doc_id = "report_q3"
    k2.embedding = None
    return [k1, k2]


@pytest.fixture
def fake_workflow():
    """Simulate a Workflow ORM row."""
    wf = MagicMock(spec=Workflow)
    wf.name = "analysis"
    wf.task_graph = {"steps": ["gather_data", "analyze", "summarize"]}
    return wf


@pytest.mark.asyncio
async def test_agent_build_context_end_to_end(
    mock_db, fake_memory_rows, fake_knowledge_rows, fake_workflow
):
    """
    Verify the full Agent context-building pipeline:
    1. Agent sends a query via Gateway.
    2. Gateway fetches Memory, Knowledge, and Workflow (graph) data.
    3. ContextEngine merges, deduplicates, and ranks items.
    4. A structured Context is returned to the Agent.
    """
    gateway = AgentGateway(mock_db)

    # --- Mock service layer DB calls ---
    # Memory search
    mem_result = MagicMock()
    mem_result.scalars.return_value.all.return_value = fake_memory_rows
    # Knowledge search
    know_result = MagicMock()
    know_result.scalars.return_value.all.return_value = fake_knowledge_rows
    # Workflow get_by_name
    wf_result = MagicMock()
    wf_result.scalar_one_or_none.return_value = fake_workflow

    async def side_effect(stmt):
        # Route mocked execute calls to the appropriate result based on statement table
        table_name = getattr(stmt, "table_name", None)
        if table_name is None:
            # Heuristic: inspect the string representation of the statement
            stmt_str = str(stmt).lower()
            if "memory" in stmt_str:
                return mem_result
            elif "knowledge" in stmt_str:
                return know_result
            elif "workflow" in stmt_str:
                return wf_result
        return MagicMock()

    mock_db.execute = AsyncMock(side_effect=side_effect)

    # --- Act: Agent asks a question through the Gateway ---
    ctx = await gateway.build_context(
        query="What happened in Q3?",
        agent_id="agent_001",
        session_id="session_abc",
        top_k=5,
    )

    # --- Assert: Context structure ---
    assert isinstance(ctx, Context)
    assert ctx.query == "What happened in Q3?"
    assert len(ctx.items) == 5  # 2 memory + 2 knowledge + 1 graph

    # --- Assert: Content sources are present ---
    sources = {item.source for item in ctx.items}
    assert sources == {"memory", "knowledge", "graph"}

    # --- Assert: Memory items contain expected metadata ---
    memory_items = [i for i in ctx.items if i.source == "memory"]
    assert len(memory_items) == 2
    assert any("concise" in i.content for i in memory_items)
    assert any(i.metadata["agent_id"] == "agent_001" for i in memory_items)

    # --- Assert: Knowledge items contain expected content ---
    knowledge_items = [i for i in ctx.items if i.source == "knowledge"]
    assert len(knowledge_items) == 2
    assert any("15%" in i.content for i in knowledge_items)

    # --- Assert: Graph/Workflow item is included ---
    graph_items = [i for i in ctx.items if i.source == "graph"]
    assert len(graph_items) == 1
    assert "gather_data" in graph_items[0].content


@pytest.mark.asyncio
async def test_agent_context_deduplication(mock_db):
    """
    Verify ContextEngine deduplicates items with the same source and content.
    Items from different sources are intentionally kept (agent needs provenance).
    """
    gateway = AgentGateway(mock_db)

    duplicate_content = "Shared fact: deadlines are Fridays."
    mem_item_a = ContextItem(source="memory", content=duplicate_content, metadata={})
    mem_item_b = ContextItem(source="memory", content=duplicate_content, metadata={})
    know_item = ContextItem(source="knowledge", content=duplicate_content, metadata={})

    with patch.object(gateway.memory, "search", new_callable=AsyncMock) as mock_mem, \
         patch.object(gateway.knowledge, "search", new_callable=AsyncMock) as mock_know, \
         patch.object(gateway.workflow, "get_by_name", new_callable=AsyncMock) as mock_wf:

        mock_mem.return_value = [mem_item_a, mem_item_b]
        mock_know.return_value = [know_item]
        mock_wf.return_value = None

        ctx = await gateway.build_context("When are deadlines?")

    # Same-source duplicates are merged; cross-source items are preserved
    assert len(ctx.items) == 2
    memory_items = [i for i in ctx.items if i.source == "memory"]
    knowledge_items = [i for i in ctx.items if i.source == "knowledge"]
    assert len(memory_items) == 1
    assert len(knowledge_items) == 1


@pytest.mark.asyncio
async def test_agent_context_ranking(mock_db):
    """
    Verify ContextEngine ranks items by score in descending order.
    """
    gateway = AgentGateway(mock_db)

    low_score = ContextItem(source="memory", content="Low priority", score=0.1)
    high_score = ContextItem(source="knowledge", content="High priority", score=0.9)
    mid_score = ContextItem(source="graph", content="Medium priority", score=0.5)

    with patch.object(gateway.memory, "search", new_callable=AsyncMock) as mock_mem, \
         patch.object(gateway.knowledge, "search", new_callable=AsyncMock) as mock_know, \
         patch.object(gateway.workflow, "get_by_name", new_callable=AsyncMock) as mock_wf:

        mock_mem.return_value = [low_score]
        mock_know.return_value = [high_score]
        mock_wf.return_value = None
        # Inject graph item manually via side-effect is tricky; instead we mock context_engine.build
        # But to keep it simple, we rely on the natural merge+rank behavior:
        # Add mid_score to memory so it enters the merge.
        mock_mem.return_value = [low_score, mid_score]

        ctx = await gateway.build_context("Ranked query")

    scores = [item.score for item in ctx.items]
    assert scores == sorted(scores, reverse=True)
    assert ctx.items[0].content == "High priority"
    assert ctx.items[1].content == "Medium priority"
    assert ctx.items[2].content == "Low priority"
