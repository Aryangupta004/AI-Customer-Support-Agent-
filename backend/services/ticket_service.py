"""Ticket Service - SupportPilot help-desk ticket lookup."""
from sqlalchemy.orm import Session
from ..db.models import Ticket
import re


class TicketService:
    """
    Service for managing and retrieving ticket information.
    Ticket IDs look like HELP-001 (any PREFIX-123 pattern is accepted).
    """

    @staticmethod
    def extract_ticket_id(text: str) -> str:
        """
        Extract ticket ID from user message.
        Looks for patterns like HELP-001, SUPPORT-123, etc.

        Args:
            text: User message

        Returns:
            Ticket ID if found, None otherwise
        """
        # Pattern matches HELP-001, SUPPORT-123, TICKET-456, etc.
        pattern = r'\b([A-Z]+-\d+)\b'
        match = re.search(pattern, text)

        if match:
            return match.group(1).upper()
        return None

    @staticmethod
    def get_ticket_by_id(db: Session, ticket_id: str) -> Ticket:
        """
        Retrieve a ticket by its ID.

        Args:
            db: Database session
            ticket_id: The ticket ID to retrieve

        Returns:
            Ticket object if found, None otherwise
        """
        try:
            ticket = db.query(Ticket).filter(
                Ticket.ticket_id == ticket_id
            ).first()
            return ticket
        except Exception as e:
            print(f"Error retrieving ticket {ticket_id}: {e}")
            return None

    @staticmethod
    def format_ticket_context(ticket: Ticket) -> str:
        """
        Format ticket information as context for the LLM.

        Args:
            ticket: Ticket object

        Returns:
            Formatted ticket information
        """
        if not ticket:
            return None

        context = f"""
Ticket ID: {ticket.ticket_id}
Title: {ticket.title}
Status: {ticket.status}
Priority: {ticket.priority}
Customer ID: {ticket.customer_id}
Description: {ticket.description}
Assigned To: {ticket.assigned_to or 'Unassigned'}
Created: {ticket.created_at}
"""

        if ticket.resolution_notes:
            context += f"Resolution Notes: {ticket.resolution_notes}\n"

        return context.strip()

    @staticmethod
    def get_all_tickets(db: Session, status: str = None) -> list:
        """
        Retrieve all tickets or filter by status.

        Args:
            db: Database session
            status: Optional status filter

        Returns:
            List of tickets
        """
        query = db.query(Ticket)

        if status:
            query = query.filter(Ticket.status == status)

        return query.all()

    @staticmethod
    def update_ticket_status(db: Session, ticket_id: str, new_status: str) -> bool:
        """
        Update ticket status (for admin purposes).

        Args:
            db: Database session
            ticket_id: Ticket ID to update
            new_status: New status value

        Returns:
            True if successful, False otherwise
        """
        try:
            ticket = db.query(Ticket).filter(
                Ticket.ticket_id == ticket_id
            ).first()

            if ticket:
                ticket.status = new_status
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating ticket {ticket_id}: {e}")
            db.rollback()
            return False


def get_ticket_service() -> TicketService:
    """Get ticket service instance (singleton pattern)"""
    return TicketService()
