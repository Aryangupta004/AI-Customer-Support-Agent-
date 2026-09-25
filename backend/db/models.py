"""SQLAlchemy models for SupportPilot AI (knowledge base, tickets, chat history)"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from .database import Base


class KnowledgeBase(Base):
    """
    Knowledge Base documents with vector embeddings.

    Embeddings are stored as JSON text and compared in Python
    (cosine similarity), so SQLite works with zero config.
    No pgvector server extension required.
    """
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    embedding = Column(Text, nullable=True)  # JSON string: "[0.1, 0.2, ...]"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Ticket(Base):
    """
    Help-desk tickets — system of record.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., HELP-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # Open, In Progress, Resolved, Closed
    priority = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    customer_id = Column(String(100), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolution_notes = Column(Text, nullable=True)
    ticket_metadata = Column(JSON, nullable=True)


class ChatHistory(Base):
    """
    Store chat messages for audit trail, including user feedback.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    ticket_id = Column(String(50), nullable=True, index=True)
    kb_docs_used = Column(Integer, nullable=True)  # Count of KB docs used
    feedback = Column(String(20), nullable=True)  # up / down / None (SupportPilot addition)
    created_at = Column(DateTime, default=datetime.utcnow)
