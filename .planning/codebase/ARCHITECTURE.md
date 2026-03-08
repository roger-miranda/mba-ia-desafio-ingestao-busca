# Architecture

**Analysis Date:** 2026-03-08

## Pattern Overview

**Overall:** Modular Pipeline Architecture with RAG (Retrieval-Augmented Generation)

**Key Characteristics:**
- Three-stage pipeline: Ingestion → Search/Retrieval → Chat/Generation
- LangChain framework for orchestrating LLM workflows
- PostgreSQL with pgvector for semantic vector storage
- Multi-LLM support (Google Generative AI and OpenAI)
- Environment-driven configuration for API keys and models

## Layers

**Ingestion Layer:**
- Purpose: Load and process PDF documents into vector embeddings for storage
- Location: `src/ingest.py`
- Contains: PDF loading, text chunking, embedding generation, vector storage
- Depends on: LangChain document loaders, embedding models (Google/OpenAI), PostgreSQL via pgvector
- Used by: Manual pipeline execution or scheduled jobs

**Search & Retrieval Layer:**
- Purpose: Query stored vectors and retrieve relevant context from ingested documents
- Location: `src/search.py`
- Contains: Prompt template definition, search chain configuration, context formatting
- Depends on: LangChain chains, vector store retrieval, LLM integration
- Used by: Chat/generation layer to augment user queries with document context

**Chat/Generation Layer:**
- Purpose: Provide conversational interface with context-aware LLM responses
- Location: `src/chat.py`
- Contains: Main entry point, user interaction loop, chain initialization
- Depends on: Search layer chain, LLM providers (Google/OpenAI)
- Used by: End-user CLI or application interface

**Infrastructure Layer:**
- Purpose: Database and vector store persistence
- Components: PostgreSQL with pgvector extension (via Docker Compose)
- Connection: Configured via `DATABASE_URL` environment variable
- Schema: pgvector collection managed via LangChain ORM

## Data Flow

**Document Ingestion Flow:**

1. Load PDF from `PDF_PATH` environment variable via LangChain PDF loader
2. Split document into chunks using LangChain text splitters
3. Generate embeddings for each chunk using configured model (Google/OpenAI)
4. Store vectors with metadata in PostgreSQL pgvector collection
5. Persist in collection named via `PG_VECTOR_COLLECTION_NAME`

**Query and Response Flow:**

1. User submits question in chat interface
2. Chat module calls `search_prompt()` from search layer
3. Search retrieves semantically similar chunks from vector store
4. Context (retrieved chunks) formatted into prompt template
5. LLM generates response constrained by CONTEXT and RULES template
6. Response returned to user, bounded to ingested document knowledge

**State Management:**
- Stateless between requests (each query is independent)
- Vector embeddings persist in PostgreSQL across sessions
- LLM context limited to current query + retrieved document chunks
- Template enforces knowledge boundary to prevent hallucination

## Key Abstractions

**Search Chain (`search.search_prompt()`):**
- Purpose: Encapsulates retrieval + prompt formatting logic
- Location: `src/search.py`
- Pattern: LangChain chain composition (retriever → prompt → LLM)
- Input: Question from user
- Output: Generated response bounded by document context

**Prompt Template (`PROMPT_TEMPLATE`):**
- Purpose: Defines constraint rules for LLM behavior
- Location: `src/search.py` lines 1-26
- Pattern: Context-constrained generation with fallback
- Rules: Only answer from context, no external knowledge, no opinions

**Vector Store Collection:**
- Purpose: Semantic search over ingested documents
- Implementation: LangChain PostgreSQL with pgvector
- Pattern: Dense vector similarity retrieval
- Indexed on: Embedding vectors from configured model

## Entry Points

**Ingestion Entry Point:**
- Location: `src/ingest.py` lines 12-13
- Triggers: Manual execution `python src/ingest.py`
- Responsibilities: Load PDF, generate embeddings, store in vector DB

**Chat Entry Point:**
- Location: `src/chat.py` lines 12-13
- Triggers: Application startup `python src/chat.py`
- Responsibilities: Initialize search chain, handle user interactions, display responses

## Error Handling

**Strategy:** Guard initialization with conditional checks, fallback to user messaging

**Patterns:**
- Chain initialization check: `if not chain` before proceeding (chat.py line 6)
- User-friendly error message on init failure (chat.py line 7)
- PDF path validation via environment variable (ingest.py line 6)

## Cross-Cutting Concerns

**Logging:** Not implemented - uses print statements for user feedback

**Validation:**
- Environment variables checked at module load time
- PDF path existence expected via configuration
- LLM API keys required via `.env`

**Authentication:**
- API key injection via environment: `GOOGLE_API_KEY`, `OPENAI_API_KEY`
- Database credentials via `DATABASE_URL` connection string
- Model selection via environment: `GOOGLE_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_MODEL`

---

*Architecture analysis: 2026-03-08*
