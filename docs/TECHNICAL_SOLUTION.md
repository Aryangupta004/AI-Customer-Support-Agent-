# How the Problem Was Solved

This document walks through the approach I took to build the customer support AI agent, from breaking down the problem to implementing each component.

## Breaking Down the Problem

The assignment asks for an AI agent that can chat with customers, look up ticket details from a system of record, and answer questions using a knowledge base. I decomposed this into three independent capabilities that get combined at query time:

1. **Knowledge base search** — given a customer's message, find the most relevant support articles.
2. **Ticket lookup** — if the customer mentions a ticket ID, fetch its details from the database.
3. **Response generation** — feed the retrieved context into an LLM to produce a helpful, grounded answer.

The orchestration layer ties these together: for every incoming message, it runs ticket extraction and KB search in parallel, merges the results, and hands everything to the LLM.

## Data Flow

Here's what happens when a user sends a message like _"I can't reset my password, ticket SUPPORT-001"_:

1. The message arrives at the FastAPI backend via the `/chat` endpoint.
2. A regex extracts the ticket ID (`SUPPORT-001`) from the text.
3. The ticket service queries PostgreSQL for that ticket's details (status, priority, description, etc.).
4. The RAG service embeds the message using SentenceTransformers, then computes cosine similarity against all KB document embeddings. Documents scoring above 0.5 are returned, ranked by relevance.
5. The LLM service builds a prompt that includes the system instructions, the ticket context, the retrieved KB content, and the user's original message.
6. The prompt is sent to Groq's API, which returns a response.
7. The interaction is saved to the `chat_history` table.
8. The response — along with metadata like which KB articles were used — goes back to the frontend.

## Implementation Details

### RAG Service

The knowledge base stores each document alongside its pre-computed embedding (a 384-dimensional vector from `all-MiniLM-L6-v2`). When a query comes in, I embed it with the same model and compute cosine similarity against every document in the database. Documents above the threshold are sorted by score and the top-k results are returned.

At this scale, brute-force similarity search is perfectly fine — it takes about 1ms per document. For a production system with thousands of articles, I'd switch to pgvector's HNSW index or a dedicated vector database.

### Ticket Service

Ticket detection uses a straightforward regex (`[A-Z]+-\d+`) to find patterns like SUPPORT-001 or JIRA-456 in the user's message. If a match is found, the service queries the tickets table by `ticket_id`. This is intentionally simple — it handles the common case cleanly and avoids overengineering.

### LLM Service

The LLM call is managed through LangChain, which handles prompt formatting and provider abstraction. The system prompt instructs the model to behave as a customer support agent, cite relevant documentation, and reference ticket details when available. The context (KB articles + ticket info) is injected into the prompt template before each call.

Using LangChain here means swapping Groq for OpenAI or a local model would only require changing the provider configuration — no prompt restructuring needed.

### Database Schema

Three tables:

- **knowledge_base** — stores title, content, category, and the embedding (as a JSON-encoded array of floats).
- **ticket** — mirrors a Jira-like schema with ticket_id, title, description, status, priority, customer_id, and assigned_to.
- **chat_history** — records each user message, the AI response, any referenced ticket ID, and how many KB docs were used.

All managed through SQLAlchemy with Alembic for migrations.

## Testing the System

I validated the system against four main scenarios:

| Scenario          | Input                               | Expected Behavior                                        |
| ----------------- | ----------------------------------- | -------------------------------------------------------- |
| KB-only query     | "How do I reset my password?"       | Retrieves password reset article, no ticket referenced   |
| Ticket-only query | "What's the status of SUPPORT-002?" | Fetches ticket details, may also pull related KB article |
| Combined          | "Billing issue, ticket SUPPORT-002" | Retrieves both ticket details and billing KB article     |
| No match          | Random unrelated text               | Generic response, no sources cited                       |

The system also exposes debug endpoints (`/debug/tickets`, `/debug/knowledge-base`, `/debug/chat-history`) so you can inspect the internal state at any time.

## Performance

Typical end-to-end response time is 2–5 seconds, with the breakdown roughly:

- Embedding the query: ~100ms
- Similarity search: ~10ms
- Database lookups: ~15ms
- LLM inference (Groq API): 1.5–4 seconds
- Overhead: ~200ms

The LLM call dominates the latency. Everything else is fast enough that optimization isn't needed at this scale.

## What I'd Do Differently in Production

- Replace in-memory similarity search with pgvector or Faiss.
- Add conversation memory so the agent can handle follow-up questions.
- Connect to a real Jira instance via its REST API instead of a mock table.
- Add authentication, rate limiting, and proper error handling.
- Cache frequent queries and their embeddings.
- Set up structured logging and monitoring.
