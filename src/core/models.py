from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class ContextItem(BaseModel):
    source: str
    content: str
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class Context(BaseModel):
    query: str
    items: List[ContextItem] = Field(default_factory=list)


# Memory schemas
class MemoryCreate(BaseModel):
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    memory_type: str
    content: str
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class MemoryOut(MemoryCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Workflow schemas
class WorkflowCreate(BaseModel):
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    task_graph: Dict[str, Any] = Field(default_factory=dict)
    decision_tree: Dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    version: Optional[str] = None
    description: Optional[str] = None
    task_graph: Optional[Dict[str, Any]] = None
    decision_tree: Optional[Dict[str, Any]] = None


class WorkflowOut(WorkflowCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Knowledge schemas
class KnowledgeCreate(BaseModel):
    doc_id: str
    chunk_content: str
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class KnowledgeUpdate(BaseModel):
    chunk_content: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class KnowledgeOut(KnowledgeCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Tool schemas
class ToolCreate(BaseModel):
    name: str
    description: Optional[str] = None
    api_schema: Optional[Dict[str, Any]] = None
    function_schema: Optional[Dict[str, Any]] = None
    permission_rules: Optional[Dict[str, Any]] = None


class ToolUpdate(BaseModel):
    description: Optional[str] = None
    api_schema: Optional[Dict[str, Any]] = None
    function_schema: Optional[Dict[str, Any]] = None
    permission_rules: Optional[Dict[str, Any]] = None


class ToolOut(ToolCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# State schemas
class StateCreate(BaseModel):
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    task_status: str = "pending"
    execution_progress: Optional[Dict[str, Any]] = None


class StateUpdate(BaseModel):
    task_status: Optional[str] = None
    execution_progress: Optional[Dict[str, Any]] = None


class StateOut(StateCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Customer schemas
class CustomerCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    status: str = "active"
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CustomerOut(CustomerCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# EmailLog schemas
class EmailLogCreate(BaseModel):
    customer_id: uuid.UUID
    direction: str
    subject: str
    content: str
    status: str = "pending"
    agent_id: Optional[str] = None
    thread_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class EmailLogUpdate(BaseModel):
    subject: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    agent_id: Optional[str] = None
    thread_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class EmailLogOut(EmailLogCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# SendEmail tool schema
class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None


class SendEmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[uuid.UUID] = None


# Gateway request/response
class BuildContextRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    top_k: int = 5
