# Mock Data Documentation

Since the assignment calls for a system of record like Jira, but connecting to a live instance would add unnecessary external dependencies, all ticket data is mocked in PostgreSQL. The knowledge base articles are also seeded locally. This makes the prototype fully self-contained and reproducible.

## Knowledge Base Documents

Four articles are seeded into the `knowledge_base` table. Each one includes a title, category, full content, and a pre-computed 384-dimensional embedding.

| #   | Title                                   | Category                | Approx. Words |
| --- | --------------------------------------- | ----------------------- | ------------- |
| 1   | How to Reset Your Password              | Account Management      | 1,200         |
| 2   | Billing, Invoices & Payment Methods     | Billing & Subscription  | 1,800         |
| 3   | API Integration & Developer Guide       | Technical Documentation | 1,000         |
| 4   | General Troubleshooting & Common Issues | Technical Support       | 1,200         |

The articles are written to resemble real support documentation — they cover step-by-step procedures, FAQs, error codes, and contact information. The content is detailed enough that the embedding model can distinguish between topics with high confidence (similarity scores above 0.8 for on-topic queries).

## Mock Tickets

Five tickets are seeded into the `ticket` table, simulating a Jira-like system of record. They cover a range of statuses, priorities, and issue types.

| Ticket ID   | Title                        | Status      | Priority | Customer |
| ----------- | ---------------------------- | ----------- | -------- | -------- |
| SUPPORT-001 | Cannot reset password        | Open        | High     | CUST-123 |
| SUPPORT-002 | Billing charge incorrect     | In Progress | Critical | CUST-456 |
| SUPPORT-003 | API authentication failing   | Open        | High     | DEV-789  |
| SUPPORT-004 | Application performance slow | In Progress | Medium   | CUST-789 |
| SUPPORT-005 | Feature request: Dark mode   | Closed      | Low      | CUST-321 |

Each ticket maps naturally to one of the KB articles, which lets the agent combine ticket context with relevant documentation when responding. SUPPORT-005 (feature request) intentionally has no KB match — this tests how the system handles cases where only ticket data is available.

## How the Data Gets Loaded

Running `python seed_db.py` from the project root:

1. Loads the `all-MiniLM-L6-v2` embedding model.
2. Inserts each KB article into the database, generating its embedding on the fly.
3. Inserts all five mock tickets.
4. Skips duplicates if the data already exists.

## Test Scenarios Covered

The mock data is designed to exercise every major code path:

| Scenario    | Example Query                           | What Happens                                       |
| ----------- | --------------------------------------- | -------------------------------------------------- |
| KB-only     | "How do I reset my password?"           | Retrieves password article, no ticket              |
| Ticket-only | "Status of SUPPORT-005?"                | Fetches closed feature request, no strong KB match |
| Combined    | "Help with billing, ticket SUPPORT-002" | Retrieves ticket + billing article                 |
| No match    | Unrelated query                         | Generic response, no sources                       |

## Verifying the Data

After seeding, you can inspect the data through the debug endpoints:

```
GET http://localhost:8000/debug/knowledge-base   → lists all KB documents
GET http://localhost:8000/debug/tickets           → lists all mock tickets
GET http://localhost:8000/debug/chat-history      → shows past interactions
```
