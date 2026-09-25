"""
Debug routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...schemas import TicketListResponse, KBListResponse, ChatHistoryResponse
from ...controllers.debug_controller import DebugController

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    status: str = Query(None, description="Filter by ticket status"),
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to list all tickets
    
    Args:
        status: Optional status filter (Open, In Progress, Resolved, Closed)
        db: Database session
        
    Returns:
        TicketListResponse with all tickets or filtered results
    """
    return DebugController.list_tickets(db, status)


@router.get("/knowledge-base", response_model=KBListResponse)
async def list_kb_documents(db: Session = Depends(get_db)):
    """
    Debug endpoint to list all knowledge base documents
    
    Args:
        db: Database session
        
    Returns:
        KBListResponse with all KB documents
    """
    return DebugController.list_kb_documents(db)


@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to retrieve chat history
    
    Args:
        limit: Number of recent chats to retrieve (1-100, default 10)
        db: Database session
        
    Returns:
        ChatHistoryResponse with recent chat interactions
    """
    return DebugController.get_chat_history(db, limit)
