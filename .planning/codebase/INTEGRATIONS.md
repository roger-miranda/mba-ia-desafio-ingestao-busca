# External Integrations

**Analysis Date:** 2026-03-08

## APIs & External Services

**LLM Providers:**
- Google Generative AI - Primary LLM and embedding generation
  - SDK/Client: `langchain-google-genai` (2.1.9)
  - Auth: `GOOGLE_API_KEY` environment variable
  - Default embedding model: `models/embedding-001`

- OpenAI - Alternative LLM and embedding provider
  - SDK/Client: `openai` (1.102.0), `langchain-openai` (0.3.30)
  - Auth: `OPENAI_API_KEY` environment variable
  - Default embedding model: `text-embedding-3-small`

## Data Storage

**Databases:**
- PostgreSQL 17
  - Connection: `DATABASE_URL` environment variable (format: postgresql://user:password@host:port/database)
  - Client: `psycopg` (3.2.9), `psycopg-pool` (3.2.6) for connection pooling
  - ORM: SQLAlchemy 2.0.43
  - Async driver: `asyncpg` (0.30.0)

**Vector Storage:**
- PostgreSQL with pgvector extension (embedded within PostgreSQL)
  - Vector collection name: `PG_VECTOR_COLLECTION_NAME` environment variable
  - Client: `langchain-postgres` (0.0.15)
  - pgvector driver: `pgvector` (0.3.6)

**File Storage:**
- Local filesystem only
  - PDF documents read from local path: `PDF_PATH` environment variable
  - Document processing: `pypdf` (6.0.0)

**Caching:**
- None detected

## Authentication & Identity

**Auth Providers:**
- Google OAuth (implicit via API key authentication)
  - Library: `google-auth` (2.40.3)
  - Protocol: gRPC-based via Google API Core

- OpenAI API Key
  - Direct API key authentication

## Monitoring & Observability

**Error Tracking:**
- LangSmith - Tracing and debugging support
  - Library: `langsmith` (0.4.20)
  - Purpose: Optional tracing of LangChain executions

**Logs:**
- Standard Python logging (no specific external service detected)
- Approach: Application-level logging via LangChain's built-in logging

## CI/CD & Deployment

**Hosting:**
- Not detected - Project appears to be a local/development application

**CI Pipeline:**
- Not detected

**Container Support:**
- Docker Compose available for local development
- PostgreSQL 17 with pgvector runs in container (image: pgvector/pgvector:pg17)
- Application itself not containerized in current setup

## Environment Configuration

**Required env vars:**
- `GOOGLE_API_KEY` - Authentication for Google Generative AI
- `GOOGLE_EMBEDDING_MODEL` - Specifies which Google embedding model to use
- `OPENAI_API_KEY` - Authentication for OpenAI
- `OPENAI_EMBEDDING_MODEL` - Specifies which OpenAI embedding model to use
- `DATABASE_URL` - PostgreSQL connection string
- `PG_VECTOR_COLLECTION_NAME` - Name of the vector collection in PostgreSQL
- `PDF_PATH` - Filesystem path to PDF document

**Secrets location:**
- `.env` file (local development, must not be committed)
- Example template: `.env.example`

## Data Flow

**Ingestion Pipeline:**
1. PDF document loaded from `PDF_PATH` (via `pypdf`)
2. Document text extracted and chunked (via `langchain-text-splitters`)
3. Text embeddings generated (via Google Generative AI or OpenAI)
4. Embeddings and metadata stored in PostgreSQL + pgvector
5. Collection name stored in `PG_VECTOR_COLLECTION_NAME`

**Search & RAG Pipeline:**
1. User query received by `search_prompt()` function (source: `src/search.py`)
2. Query embedded using same embedding model as ingestion
3. Vector similarity search performed against PostgreSQL pgvector store
4. Retrieved context passed to LLM via prompt template (defined in `src/search.py`)
5. LLM (Google or OpenAI) generates response constrained to retrieved context
6. Response returned to user via chat interface (`src/chat.py`)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- Potential server-sent events support via `httpx-sse` (0.4.1), but not actively used in current codebase

## Integration Points in Codebase

**Primary Integration Files:**
- `src/ingest.py` - PDF ingestion pipeline (currently stub, calls `ingest_pdf()`)
- `src/search.py` - Search and prompt management (defines `PROMPT_TEMPLATE` and `search_prompt()`)
- `src/chat.py` - Chat interface orchestration (calls `search_prompt()` from search module)

---

*Integration audit: 2026-03-08*
