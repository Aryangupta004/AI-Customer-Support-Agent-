"""
Debug controller - handles debug operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..services.ticket_service import get_ticket_service
from ..services.rag_service import get_rag_service
from ..db.models import ChatHistory
from ..schemas import TicketListResponse, KBListResponse, ChatHistoryResponse, TicketInfo, KBDocument, ChatHistoryEntry


class DebugController:
    """Controller for debug operations"""
    
    @staticmethod
    def list_tickets(db: Session, status: str = None) -> TicketListResponse:
        """
        List all tickets or filter by status
        
        Args:
            db: Database session
            status: Optional status filter
            
        Returns:
            TicketListResponse with tickets
        """
        ticket_service = get_ticket_service()
        tickets = ticket_service.get_all_tickets(db, status)
        
        ticket_list = [
            TicketInfo(
                ticket_id=t.ticket_id,
                title=t.title,
                status=t.status,
                priority=t.priority,
                customer_id=t.customer_id
            )
            for t in tickets
        ]
        
        return TicketListResponse(count=len(ticket_list), tickets=ticket_list)
    
    @staticmethod
    def list_kb_documents(db: Session) -> KBListResponse:
        """
        List all knowledge base documents
        
        Args:
            db: Database session
            
        Returns:
            KBListResponse with documents
        """
        rag_service = get_rag_service()
        docs = rag_service.get_all_kb_documents(db)
        
        doc_list = [
            KBDocument(
                id=doc.id,
                title=doc.title,
                category=doc.category,
                created_at=str(doc.created_at)
            )
            for doc in docs
        ]
        
        return KBListResponse(count=len(doc_list), documents=doc_list)
    
    @staticmethod
    def get_chat_history(db: Session, limit: int = 10) -> ChatHistoryResponse:
        """
        Get recent chat history
        
        Args:
            db: Database session
            limit: Number of recent chats to retrieve
            
        Returns:
            ChatHistoryResponse with recent chats
        """
        chats = db.query(ChatHistory).order_by(
            desc(ChatHistory.created_at)
        ).limit(limit).all()
        
        chat_list = [
            ChatHistoryEntry(
                id=c.id,
                user_message=c.user_message[:100],  # Truncate for display
                ticket_id=c.ticket_id,
                kb_docs_used=c.kb_docs_used,
                created_at=str(c.created_at)
            )
            for c in chats
        ]
        
        return ChatHistoryResponse(count=len(chat_list), chats=chat_list)
