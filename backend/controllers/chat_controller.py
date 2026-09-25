"""Chat controller - SupportPilot AI business logic."""
from sqlalchemy.orm import Session
from pathlib import Path
from ..db.models import ChatHistory
from ..services.llm_service import get_llm_service
from ..services.ticket_service import get_ticket_service
from ..services.rag_service import get_rag_service
from ..schemas import ChatResponse, SourceReference


class ChatController:
    """Controller for SupportPilot chat operations."""

    @staticmethod
    def process_chat(user_message: str, db: Session) -> ChatResponse:
        """
        Process user message and generate a support response.

        Pipeline: ticket lookup -> KB vector search -> prompt build ->
        LLM (or offline fallback) -> persist -> respond.
        """
        # Validate input
        if not user_message or not user_message.strip():
            raise ValueError("Message cannot be empty")

        user_message = user_message.strip()

        # Initialize services
        ticket_service = get_ticket_service()
        rag_service = get_rag_service()
        llm_service = get_llm_service()

        # ==================== Step 1: Ticket lookup ====================
        ticket_id = ticket_service.extract_ticket_id(user_message)
        ticket_context = None
        ticket_info = None

        if ticket_id:
            ticket_info = ticket_service.get_ticket_by_id(db, ticket_id)
            if ticket_info:
                ticket_context = ticket_service.format_ticket_context(ticket_info)

        # ==================== Step 2: Knowledge-base search ====================
        kb_context, kb_docs = rag_service.get_relevant_docs_for_query(db, user_message)

        # ==================== Step 3: System prompt ====================
        prompt_path = Path(__file__).parent.parent / "prompts" / "support_agent_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_system_prompt = f.read()

        context_instructions = ""

        if ticket_context:
            context_instructions += f"\nMATCHED TICKET:\n{ticket_context}\n"

            # Add priority-based instructions
            if ticket_info and ticket_info.priority == "Critical":
                context_instructions += "\nThis is a CRITICAL priority ticket. Treat it as urgent.\n"

        if kb_context:
            context_instructions += f"\nRELEVANT HELP ARTICLES:\n{kb_context}\n"
        else:
            context_instructions += "\nNo relevant help articles found for this query.\n"

        system_prompt = base_system_prompt + context_instructions

        # ==================== Step 4: Generate response ====================
        ai_response = llm_service.generate_response(system_prompt, user_message)

        # ==================== Step 5: Persist chat ====================
        chat_entry = ChatHistory(
            user_message=user_message,
            ai_response=ai_response,
            ticket_id=ticket_id,
            kb_docs_used=len(kb_docs),
        )
        db.add(chat_entry)
        db.commit()

        # ==================== Step 6: Build API response ====================
        sources = [
            SourceReference(title=doc.title, category=doc.category)
            for doc in kb_docs
        ]

        return ChatResponse(
            response=ai_response,
            ticket_id=ticket_id,
            kb_docs_used=len(kb_docs),
            sources=sources,
        )
