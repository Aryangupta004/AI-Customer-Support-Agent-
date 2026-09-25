"""
Chat routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...schemas import ChatRequest, ChatResponse
from ...controllers.chat_controller import ChatController

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for customer support
    
    Process:
    1. Extract ticket ID from user message (if present)
    2. Retrieve ticket details if ticket ID found
    3. Search knowledge base for relevant documents
    4. Combine contexts and generate response using LLM
    5. Store interaction in chat history
    
    Args:
        request: ChatRequest with user message
        db: Database session
        
    Returns:
        ChatResponse with AI response and metadata
        
    Raises:
        HTTPException: If message is empty or processing fails
    """
    try:
        response = ChatController.process_chat(request.message, db)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
