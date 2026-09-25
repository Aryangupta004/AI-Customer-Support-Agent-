#!/usr/bin/env python3
"""
Seed SupportPilot AI database (thin wrapper — single source of truth
lives in backend/db/seed_data.py).
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from db.seed_data import seed_database


if __name__ == "__main__":
    print("Seeding SupportPilot AI database...")
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        from db.database import drop_db

        print("Resetting database...")
        drop_db()
    seed_database()
