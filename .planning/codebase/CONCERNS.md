# Codebase Concerns

**Analysis Date:** 2026-03-08

## Critical Implementation Gaps

**Incomplete Core Modules:**
- Issue: All three primary modules (`ingest.py`, `chat.py`, `search.py`) contain only stub implementations with empty function bodies
- Files: `src/ingest.py`, `src/chat.py`, `src/search.py`
- Impact: No actual functionality implemented. The application cannot ingest PDFs, search documents, or chat with the system. This is a complete blocker for the project
- Fix approach: Implement the core business logic for each module:
  - `ingest.py`: Implement PDF loading, text extraction, chunking, and embedding generation
  - `search.py`: Implement RAG prompt construction and LLM chain setup
  - `chat.py`: Implement interactive chat loop with user input handling

## Test Coverage Gaps

**Complete Absence of Tests:**
- What's not tested: All functionality
- Files: `src/ingest.py`, `src/chat.py`, `src/search.py`
- Risk: No test coverage exists. This means any implementation changes are at high risk of breaking functionality without automated detection
- Priority: High - Essential before production deployment

## Configuration & Environment Management

**Incomplete Environment Configuration:**
- Issue: `.env.example` file exists but lacks critical configuration details and no validation/defaults are implemented
- Files: `.env.example`, `src/ingest.py`, `src/chat.py`
- Impact: Required env vars (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `PDF_PATH`) are loaded but never validated. Missing vars will cause runtime failures rather than clear startup errors
- Fix approach: Implement environment validation using pydantic-settings (which is already in dependencies) to validate and provide helpful errors at startup

**Missing Configuration Documentation:**
- Issue: `.env.example` lacks descriptions for each configuration variable
- Files: `.env.example`
- Impact: Developers don't know which API providers to choose or what values each variable requires
- Fix approach: Add comments explaining each variable's purpose, format, and where to obtain it

## Dependency Management Concerns

**Heavy Dependency on AI/ML Libraries:**
- Risk: Large number of transitive dependencies for LLM integration (langchain, google-genai, openai, langchain-postgres)
- Files: `requirements.txt`
- Impact: Large attack surface, potential supply chain risks, slow installation, difficult debugging of LLM-related issues
- Current mitigation: Dependencies are pinned to specific versions, which is good
- Recommendations:
  - Implement dependency scanning in CI/CD
  - Use `pip-audit` or similar to check for known vulnerabilities
  - Consider dependency consolidation where possible

**Dual Package Manager Dependencies:**
- Issue: Both `psycopg2-binary` and `psycopg` (without binary) are present, as well as multiple psycopg versions (`psycopg==3.2.9`, `psycopg-pool==3.2.6`, `psycopg-binary==3.2.9`)
- Files: `requirements.txt` (lines 49-52)
- Impact: Redundant dependencies increase package size and could cause subtle bugs if different psycopg versions behave differently
- Fix approach: Consolidate to use only psycopg (non-binary) with psycopg-pool, remove psycopg2-binary

**Unclear Embedding Model Selection:**
- Issue: Both Google AI and OpenAI embedding models are configured via environment variables, but no logic exists to select which one to use
- Files: `.env.example`, `src/search.py` (once implemented)
- Impact: Ambiguity during implementation - developers won't know which embedding provider should be the default or how to switch between them
- Fix approach: Implement clear logic for embedding provider selection with sensible defaults

## Integration Architecture Concerns

**Hard-coded Postgres Credentials in Docker Compose:**
- Issue: `docker-compose.yml` contains hardcoded PostgreSQL password "postgres" in multiple places
- Files: `docker-compose.yml` (lines 7-8, 27)
- Impact: Security risk if docker-compose is used in production, though acceptable for development/demo
- Current mitigation: This is clearly marked as dev environment (container name: postgres_rag)
- Recommendations:
  - Document that this is for development only
  - Create a production docker-compose.yml or use proper secret management

**Missing Database Schema & Initialization:**
- Issue: Database vector extension is bootstrapped, but no table schemas, indexes, or LangChain vector store initialization is documented or scripted
- Files: `docker-compose.yml` (bootstrap_vector_ext service creates extension, but nothing more), `src/ingest.py` (where schema setup would occur)
- Impact: The application cannot run without manual database setup. First ingestion will fail without proper tables
- Fix approach: Create database initialization script that runs automatically, either as part of ingest.py or as a separate setup step

## Import & Module Organization Issues

**Relative Import Without Package Structure:**
- Issue: `chat.py` uses `from search import search_prompt` (relative import) without proper package initialization
- Files: `src/chat.py` (line 1), `src/search.py`
- Impact: Module discovery will fail if the src directory is not in PYTHONPATH or if modules are imported differently during testing
- Fix approach: Use proper package imports with absolute paths (e.g., `from src.search import search_prompt`) and create `src/__init__.py`

## Error Handling Gaps

**Minimal Error Handling:**
- Issue: `chat.py` has one error check (line 6-8) but it doesn't specify what errors should occur or how to handle them from other modules
- Files: `src/chat.py`
- Impact: When functions fail (e.g., API timeouts, database connection errors), errors will bubble up ungracefully with unclear messages
- Fix approach: Implement specific exception handling for:
  - PDF processing errors in `ingest.py`
  - LLM API failures in `search.py`
  - Database connection issues in both modules

## Data Validation Gaps

**No Input Validation:**
- Issue: `search_prompt()` accepts an optional `question` parameter but has no validation logic
- Files: `src/search.py` (line 28)
- Impact: Invalid or malicious input (very long strings, special characters) could cause API calls to fail or produce unexpected behavior
- Fix approach: Validate question length and content before passing to LLM chains

**Unclear Prompt Injection Prevention:**
- Issue: The prompt template in `search.py` attempts to constrain responses but no escaping or sanitization of user input is visible in the stub
- Files: `src/search.py` (lines 1-26)
- Impact: User input is directly interpolated into the prompt (line 23: `{pergunta}`). Without sanitization, prompt injection attacks are possible
- Fix approach: Implement input sanitization and consider using structured prompt formats from langchain

## Scaling & Performance Concerns

**No Pagination or Result Limiting:**
- Issue: Search implementation will likely retrieve all matching vectors from database without limiting results
- Files: `src/search.py` (once implemented)
- Impact: Large document collections will slow down query performance and exceed token limits for LLMs
- Fix approach: Implement k-value limiting for vector similarity search (typically 3-5 most relevant documents)

**Missing Chunking Strategy Documentation:**
- Issue: PDF documents will need to be chunked for embedding, but no strategy is documented or implemented
- Files: `src/ingest.py` (line 8-9)
- Impact: Poor chunking (too large or too small) will degrade search relevance
- Fix approach: Implement configurable chunk size and overlap with sensible defaults (e.g., 1000-2000 token chunks with 200-token overlap)

## Incomplete Project Setup

**Empty Main README:**
- Issue: `README.md` is nearly empty - only contains a template instruction
- Files: `README.md`
- Impact: No instructions for setup, running the application, or understanding the project structure
- Fix approach: Document setup steps, dependencies, running instructions, and project overview

**No Entry Point Script:**
- Issue: No main orchestration script exists to coordinate the three modules (ingest, search, chat)
- Files: None - this needs to be created
- Impact: Users won't know how to run the complete workflow
- Fix approach: Create a main.py or run_pipeline.sh that:
  1. Validates environment configuration
  2. Initializes database
  3. Ingests PDF if not already ingested
  4. Starts chat interface

## Security Concerns

**API Key Exposure Risk:**
- Issue: No protection against printing/logging API keys during debugging
- Files: `src/ingest.py`, `src/chat.py`, `src/search.py`
- Impact: Developers might accidentally commit logs containing API keys
- Current mitigation: `.gitignore` should exclude `.env` files (check if it does)
- Recommendations:
  - Implement debug logging that masks sensitive values
  - Use logging framework instead of print statements
  - Document secure development practices

**Unvalidated External API Responses:**
- Issue: No visible error handling or validation of LLM API responses
- Files: `src/search.py` (once implemented)
- Impact: Unexpected API responses (rate limits, errors) could cause unhandled exceptions
- Fix approach: Implement try-catch blocks with graceful degradation for API failures

## Documentation & Knowledge Transfer

**No Architecture Documentation:**
- Issue: Complex architecture (PDF ingestion → embeddings → vector DB → RAG) exists conceptually but is not documented anywhere in the repo
- Files: All modules lack docstrings and architecture explanation
- Impact: Future developers cannot understand the intended data flow or module responsibilities
- Fix approach: Create detailed architecture documentation covering:
  - Data flow from PDF to user response
  - Embedding strategy and model selection
  - Vector database schema and querying
  - LLM integration points and fallback strategies

---

*Concerns audit: 2026-03-08*
