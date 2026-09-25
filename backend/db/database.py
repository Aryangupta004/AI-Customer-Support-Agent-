"""Database configuration and connection setup (SupportPilot AI)"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Default to local SQLite so the project runs with zero config.
# Override with Postgres, e.g.:
#   DATABASE_URL=postgresql://postgres:<password>@localhost:5432/supportpilot
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./supportpilot.db")

# SQLite needs check_same_thread=False; resolve relative path against repo root.
_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
    if DATABASE_URL in ("sqlite:///./supportpilot.db", "sqlite:///supportpilot.db"):
        root = Path(__file__).resolve().parents[2]
        DATABASE_URL = f"sqlite:///{root / 'supportpilot.db'}"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Useful for testing, not recommended for production
    echo=False,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create all tables"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized successfully ({DATABASE_URL})")


def drop_db():
    """Drop all tables (for testing purposes)"""
    Base.metadata.drop_all(bind=engine)
    print("Database dropped")
