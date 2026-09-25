#!/usr/bin/env python3
"""
Initialize SupportPilot AI database tables.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from db.database import engine, Base, init_db, DATABASE_URL
from db.models import KnowledgeBase, Ticket, ChatHistory

if __name__ == "__main__":
    print("Initializing SupportPilot AI database...")
    print(f"Target: {DATABASE_URL}")
    try:
        init_db()
        print("Database initialized successfully!")
        print("Tables created:")
        print("   - knowledge_base")
        print("   - tickets")
        print("   - chat_history")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
