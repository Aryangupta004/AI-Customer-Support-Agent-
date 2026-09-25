"""Pydantic schemas for SupportPilot AI request/response validation."""
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'm having trouble logging in. My ticket is HELP-001"
            }
        }


class SourceReference(BaseModel):
    """Knowledge base source reference"""
    title: str
    category: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    ticket_id: Optional[str] = None
    kb_docs_used: int = 0
    sources: Optional[List[SourceReference]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str


class SystemInfoResponse(BaseModel):
    """System information response"""
    name: str
    version: str
    llm_model: str
    embedding_model: str
    database: str


class TicketInfo(BaseModel):
    """Ticket information"""
    ticket_id: str
    title: str
    status: str
    priority: str
    customer_id: str


class TicketListResponse(BaseModel):
    """List of tickets response"""
    count: int
    tickets: List[TicketInfo]


class KBDocument(BaseModel):
    """Knowledge base document info"""
    id: int
    title: str
    category: str
    created_at: str


class KBListResponse(BaseModel):
    """List of KB documents response"""
    count: int
    documents: List[KBDocument]


class ChatHistoryEntry(BaseModel):
    """Chat history entry"""
    id: int
    user_message: str
    ticket_id: Optional[str]
    kb_docs_used: Optional[int]
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    count: int
    chats: List[ChatHistoryEntry]
