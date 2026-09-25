"""Seed database with SupportPilot help articles and tickets."""
from sentence_transformers import SentenceTransformer
from .database import SessionLocal, init_db, drop_db
from .models import KnowledgeBase, Ticket
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Help articles (SupportPilot edition — HELP prefix)
KB_DOCUMENTS = [
    {
        "title": "Getting Started with SupportPilot",
        "content": """
        Welcome to SupportPilot, your personal AI help-desk.

        1. Type a question in the chat box, e.g. "How do I reset my password?"
        2. To check a ticket, mention its ID like HELP-001.
        3. Open "Knowledge Base Sources" under any answer to see citations.
        4. Use the sidebar Debug Info to inspect backend status.
        5. Give thumbs up/down feedback — it is stored with chat history.

        No API key? The app runs in offline demo mode and still shows
        ticket + article matches.
        """,
        "category": "Getting Started",
    },
    {
        "title": "How to Reset Your Password",
        "content": """
        If you've forgotten your password or need to reset it:

        1. Navigate to the login page and click 'Forgot Password'
        2. Enter the email address associated with your account
        3. Check your email for a password reset link
        4. Click the link and set a new password
        5. Make sure your new password is at least 8 characters long
        6. Include at least one uppercase letter, one number, and one special character

        If you don't receive the email within 5 minutes, check your spam folder or try again.
        """,
        "category": "Account Management",
    },
    {
        "title": "Billing and Subscription Issues",
        "content": """
        Common billing questions:

        Q: Why was I charged?
        A: You may have been charged for your subscription renewal. Check your subscription settings in Account > Billing.

        Q: How do I upgrade my plan?
        A: Go to Settings > Plans and select the plan that best fits your needs. Your card will be charged immediately.

        Q: Can I get a refund?
        A: We offer full refunds within 14 days of purchase. Contact support with your order number.

        Q: How do I cancel my subscription?
        A: Go to Account > Billing > Subscriptions and click Cancel. Your access will continue until the end of your billing period.

        For payment issues, ensure your card information is up to date and try again.
        """,
        "category": "Billing",
    },
    {
        "title": "Getting Started with API Integration",
        "content": """
        To integrate our API into your application:

        1. Get an API key from your dashboard (Settings > Developer > API Keys)
        2. Store your API key securely in environment variables
        3. Use the base URL: https://api.example.com/v1/

        Example request:
        curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/data

        Authentication:
        - All requests must include the Authorization header
        - Use Bearer token authentication
        - Include your API key in the header: Authorization: Bearer your_api_key

        Rate limits: 1000 requests per hour for free tier

        For detailed documentation, visit: https://docs.example.com/api
        """,
        "category": "Technical",
    },
    {
        "title": "Troubleshooting Connection Issues",
        "content": """
        If you're experiencing connection problems:

        1. Check your internet connection
        2. Try clearing your browser cache and cookies
        3. Disable browser extensions that might interfere
        4. Try accessing from a different device or network
        5. Check our status page at status.example.com

        Common error codes:
        - 502 Bad Gateway: Server is temporarily unavailable, try again in a few minutes
        - 503 Service Unavailable: Maintenance in progress, check status page
        - 504 Gateway Timeout: Request took too long, try again

        If issues persist, please contact support with:
        - Your browser and version
        - Steps you've taken to troubleshoot
        - Screenshot or error message
        - Your approximate location
        """,
        "category": "Technical",
    },
]

# Help-desk tickets (HELP-xxx series)
MOCK_TICKETS = [
    {
        "ticket_id": "HELP-001",
        "title": "Account Login Not Working",
        "description": "User reports they cannot log in with their email and password. They've confirmed the credentials are correct.",
        "status": "Open",
        "priority": "High",
        "customer_id": "CUST-12345",
        "assigned_to": "john.doe@company.com",
        "resolution_notes": None,
    },
    {
        "ticket_id": "HELP-002",
        "title": "Billing charged twice",
        "description": "Customer was charged twice for their monthly subscription. They need a refund for the duplicate charge.",
        "status": "In Progress",
        "priority": "Critical",
        "customer_id": "CUST-67890",
        "assigned_to": "jane.smith@company.com",
        "resolution_notes": "Reviewing transaction history. Likely due to double-click during payment.",
    },
    {
        "ticket_id": "HELP-003",
        "title": "API rate limit questions",
        "description": "Customer is hitting rate limits on the free tier and wants to know about upgrading.",
        "status": "Open",
        "priority": "Medium",
        "customer_id": "CUST-55555",
        "assigned_to": "alice.johnson@company.com",
        "resolution_notes": None,
    },
    {
        "ticket_id": "HELP-004",
        "title": "Missing data in export",
        "description": "Customer requested a data export but some records are missing from the CSV.",
        "status": "Resolved",
        "priority": "Medium",
        "customer_id": "CUST-99999",
        "assigned_to": "bob.wilson@company.com",
        "resolution_notes": "Re-exported with corrected date filters. Issue was user filtering incorrectly.",
    },
    {
        "ticket_id": "HELP-005",
        "title": "Feature request: Dark mode",
        "description": "Multiple customers requesting dark mode theme for the UI.",
        "status": "Open",
        "priority": "Low",
        "customer_id": "CUST-44444",
        "assigned_to": None,
        "resolution_notes": None,
    },
    {
        "ticket_id": "HELP-006",
        "title": "SupportPilot onboarding",
        "description": "New user wants a tour of SupportPilot offline mode vs online Groq answers.",
        "status": "Open",
        "priority": "Low",
        "customer_id": "CUST-ARYAN",
        "assigned_to": None,
        "resolution_notes": None,
    },
]


def generate_embeddings(text: str, model: SentenceTransformer) -> str:
    """Generate embeddings for text and return as JSON string"""
    embedding = model.encode(text, convert_to_numpy=True)
    return json.dumps(embedding.tolist())


def seed_database():
    """Populate database with mock data"""
    # Initialize database
    init_db()

    # Load embedding model
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    print(f"Loading embedding model: {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_kb = db.query(KnowledgeBase).first()
        existing_tickets = db.query(Ticket).first()

        if existing_kb or existing_tickets:
            print("Database already seeded. Skipping...")
            return

        # Add knowledge base documents
        print("Seeding knowledge base documents...")
        for doc in KB_DOCUMENTS:
            # Generate embedding for the document
            combined_text = f"{doc['title']} {doc['content']}"
            embedding = generate_embeddings(combined_text, embedding_model)

            kb_entry = KnowledgeBase(
                title=doc["title"],
                content=doc["content"],
                category=doc["category"],
                embedding=embedding,
            )
            db.add(kb_entry)

        db.commit()
        print(f"Added {len(KB_DOCUMENTS)} knowledge base documents")

        # Add tickets
        print("Seeding mock tickets...")
        for ticket in MOCK_TICKETS:
            ticket_entry = Ticket(**ticket)
            db.add(ticket_entry)

        db.commit()
        print(f"Added {len(MOCK_TICKETS)} mock tickets")

        print("Database seeding completed successfully!")

    except IntegrityError as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("Resetting database...")
        drop_db()
        print("Database reset. Now seeding...")

    seed_database()
