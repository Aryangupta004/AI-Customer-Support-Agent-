# SupportPilot AI

A personal AI help-desk assistant built on Retrieval-Augmented Generation (RAG). Ask questions, mention a ticket like `HELP-001`, and get grounded answers with cited help articles. Runs fully offline for demo, or with Groq for full LLM answers.

> Forked and personalized from a generic customer-support RAG template. Differences: **SupportPilot branding**, `HELP-xxx` ticket series + onboarding article, **SQLite-by-default** (no Postgres/pgvector setup), **offline fallback** when no API key is set, feedback buttons, friendlier prompt, and `2.0.0-personal` API.

## How It Works

1. You ask in the Streamlit chat UI.
2. Ticket IDs (`HELP-001`, `SUPPORT-123`, any `PREFIX-123`) are extracted via regex.
3. The KB is searched with local `all-MiniLM-L6-v2` embeddings + cosine similarity (pure Python — no pgvector server needed).
4. Ticket + KB context is injected into the system prompt.
5. Groq (`openai/gpt-oss-20b`) answers — or the built-in offline extractive fallback answers if no key is set.
6. The turn is saved to `chat_history` and sources are shown in the UI.

## Architecture

- **Frontend:** Streamlit (`ui/app.py`) — chat, sources, debug sidebar, 👍/👎 feedback
- **Backend:** FastAPI (`backend/`) — `/api/chat`, `/health`, `/info`, `/debug/*`
- **Services:** `rag_service` (embeddings/search), `ticket_service` (regex + lookup), `llm_service` (Groq + offline fallback)
- **DB:** SQLite `supportpilot.db` by default; Postgres optional. Tables: `knowledge_base`, `tickets`, `chat_history`
- **Embeddings:** SentenceTransformers locally; stored as JSON text

## Requirements

- Python 3.9+ (tested 3.13)
- No database server needed (SQLite default)
- Optional: Groq API key for full AI answers; Postgres if you outgrow SQLite

## Fresh Setup (Windows PowerShell)

```powershell
# 1. Virtual env
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Dependencies
.\venv\Scripts\pip install -r backend/requirements.txt

# 3. Env
Copy-Item .env.example .env
# Optional: add GROQ_API_KEY to .env for online answers

# 4. Database (SQLite, zero-config)
.\venv\Scripts\python init_db.py
.\venv\Scripts\python seed_db.py --reset

# 5. Backend (Terminal 1)
.\venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 6. UI (Terminal 2)
.\venv\Scripts\streamlit run ui/app.py

# 7. Open http://localhost:8501
```

Postgres (optional):
```powershell
# in .env:
# DATABASE_URL=postgresql://postgres:<password>@localhost:5432/supportpilot
.\venv\Scripts\python init_db.py
.\venv\Scripts\python seed_db.py --reset
```

## Try It

| Type | Example |
| ---- | ------- |
| Onboarding | "What is SupportPilot?" |
| Knowledge base | "How do I reset my password?" |
| Ticket lookup | "What's the status of HELP-002?" |
| Combined | "I was charged twice — ticket HELP-002" |

API: `GET /health`, `GET /info`, `POST /api/chat`, `GET /debug/tickets`, `GET /debug/knowledge-base`, `GET /debug/chat-history`. Docs at `http://127.0.0.1:8000/docs`.

## Project Structure

```
supportpilot-ai/
├── backend/
│   ├── main.py / app.py        # entry + factory (SupportPilot branded)
│   ├── api/endpoints/          # chat, health, debug
│   ├── controllers/            # chat orchestration
│   ├── services/               # rag, ticket, llm (+offline fallback)
│   ├── db/                     # database.py (sqlite default), models, seed_data
│   └── prompts/                # SupportPilot system prompt
├── ui/app.py                   # Streamlit chat (rebranded + feedback)
├── init_db.py / seed_db.py     # fresh DB setup (HELP-xxx data)
├── supportpilot.db             # created on init (gitignored)
├── .env / .env.example
└── docs/
```

## Notes

- RAG threshold default `0.35` (lowered from `0.5`) so short demo queries still match.
- Old `SUPPORT-xxx` IDs still parse (regex is generic), but seed data is now `HELP-001..006`.
- Alembic files are legacy and not used for fresh setup; `init_db.py` (`create_all`) is the path.
