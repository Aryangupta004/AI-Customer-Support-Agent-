# Assumptions and Design Decisions

This document captures the key assumptions I made while building the customer support AI agent, along with the reasoning behind each decision.

## Ticket System

The problem statement mentions Jira or a similar system for ticket management. Rather than integrating with a live Jira instance — which would introduce external dependencies and require credentials — I simulated the system of record using a PostgreSQL table with a realistic schema (ticket ID, status, priority, assignee, description, etc.). This keeps the prototype self-contained and fully reproducible.

Ticket IDs are extracted from user messages using a simple regex pattern (`[A-Z]+-\d+`), which matches standard formats like SUPPORT-001 or JIRA-123. This is deterministic and fast — no ML model needed for extraction.

## Knowledge Retrieval (RAG over Fine-tuning)

I chose Retrieval-Augmented Generation instead of fine-tuning because it handles a dynamic knowledge base without retraining. When the KB changes, you just re-embed the new documents. It also makes the system more transparent — you can see exactly which articles were retrieved and why, which matters for customer support.

Embeddings are generated locally using `all-MiniLM-L6-v2` from SentenceTransformers. It's small (~100MB), runs fast (~100ms per query), and produces 384-dimensional vectors that work well for general-purpose semantic search. No external API call is needed for embeddings.

For similarity search, I compute cosine similarity in-memory against all stored document embeddings. At prototype scale (a handful of documents), this is negligible in cost. For production with thousands of documents, you'd swap this for pgvector's native indexing or a dedicated vector store like Faiss.

The similarity threshold is set at 0.5 — a reasonable middle ground between catching relevant documents and filtering out noise.

## LLM Choice

I used Groq's free-tier API with `llama-3.1-8b-instant`. It's fast, free, and good enough for this task. The LLM service is built with LangChain, which makes it straightforward to swap in another provider (OpenAI, Anthropic, local model) if needed.

## Database

PostgreSQL serves as the single data store for the knowledge base, tickets, and chat history. Using one database avoids consistency issues across services and keeps the setup simple. Embeddings are stored as JSON strings rather than pgvector's native type — this trades some query performance for easier debugging and broader PostgreSQL version compatibility.

Chat history is stored for audit purposes but is not fed back into subsequent queries. Each message is treated independently (no multi-turn conversation memory). Adding conversation context would be a natural next step.

## Frontend

Streamlit was chosen for the UI. It has built-in chat components, requires minimal code, and stays in Python — no need for a separate JavaScript frontend. It's well suited for prototyping but wouldn't be the choice for a production customer-facing application.

## Security

This is a demo environment. There's no authentication, CORS is open, and the API key lives in a `.env` file. In production, you'd add JWT-based auth, HTTPS, restricted CORS, rate limiting, and a proper secrets manager.

## Scope

The system is sized for a single user running locally. The mock data — 4 KB articles and 5 tickets — is enough to demonstrate all the key scenarios: KB-only queries, ticket-only lookups, combined context queries, and no-match fallbacks.

## Technology Summary

| Component     | Choice               | Why                                         |
| ------------- | -------------------- | ------------------------------------------- |
| Backend       | FastAPI              | Async, fast, auto-generates API docs        |
| Database      | PostgreSQL           | Mature, supports vectors, single data store |
| LLM           | Groq (Llama 3.1)     | Free tier, fast inference                   |
| Embeddings    | SentenceTransformers | Runs locally, no API dependency             |
| Frontend      | Streamlit            | Quick to build, Python-native               |
| ORM           | SQLAlchemy + Alembic | Industry standard, migration support        |
| LLM Framework | LangChain            | Provider-agnostic, easy to swap models      |
