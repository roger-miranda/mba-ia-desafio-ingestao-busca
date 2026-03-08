# Technology Stack

**Analysis Date:** 2026-03-08

## Languages

**Primary:**
- Python 3.x - Core application for PDF ingestion, document search, and RAG chat functionality

## Runtime

**Environment:**
- Python runtime (version not explicitly specified in requirements.txt, infer from dependency compatibility)

**Package Manager:**
- pip
- Lockfile: requirements.txt (pinned versions)

## Frameworks

**Core:**
- LangChain 0.3.27 - LLM orchestration and RAG framework
- LangChain Community 0.3.27 - Extended LangChain integrations
- LangChain Google GenAI 2.1.9 - Google AI/Gemini integration
- LangChain OpenAI 0.3.30 - OpenAI integration
- LangChain Postgres 0.0.15 - PostgreSQL vector store integration

**Database & Vector Storage:**
- SQLAlchemy 2.0.43 - ORM for database operations
- asyncpg 0.30.0 - Async PostgreSQL driver
- psycopg 3.2.9 - PostgreSQL adapter
- psycopg-pool 3.2.6 - Connection pooling for PostgreSQL
- pgvector 0.3.6 - PostgreSQL vector extension client

**Async/HTTP:**
- aiohttp 3.12.15 - Async HTTP client/server
- httpx 0.28.1 - Modern HTTP client with async support
- httpcore 1.0.9 - Low-level HTTP client
- httpx-sse 0.4.1 - Server-Sent Events support for httpx

**Document Processing:**
- pypdf 6.0.0 - PDF parsing and manipulation
- filetype 1.2.0 - File type detection

**Configuration & Environment:**
- python-dotenv 1.1.1 - Environment variable loading from .env files
- pydantic 2.11.7 - Data validation and settings management
- pydantic-settings 2.10.1 - Pydantic integration for application settings

**API Clients:**
- openai 1.102.0 - OpenAI API client
- google-api-core 2.25.1 - Google API client library
- google-auth 2.40.3 - Google authentication library
- google-ai-generativelanguage 0.6.18 - Google Generative AI protocol library
- grpcio 1.74.0 - gRPC framework for distributed systems
- grpcio-status 1.74.0 - gRPC status codes and utilities

**Data Processing & Serialization:**
- dataclasses-json 0.6.7 - JSON serialization for dataclasses
- orjson 3.11.3 - Fast JSON serialization
- jsonpatch 1.33 - JSON Patch RFC 6902 implementation
- jsonpointer 3.0.0 - JSON Pointer RFC 6901 implementation
- marshmallow 3.26.1 - Object serialization/deserialization

**Text Processing & Embeddings:**
- tiktoken 0.11.0 - Token counter for OpenAI models
- langchain-text-splitters 0.3.9 - Text chunking utilities
- regex 2025.7.34 - Advanced regex patterns

**Utilities & Dependencies:**
- requests 2.32.5 - HTTP library
- requests-toolbelt 1.0.0 - HTTP utilities
- tenacity 9.1.2 - Retry logic
- cachetools 5.5.2 - Caching utilities
- tqdm 4.67.1 - Progress bars
- PyYAML 6.0.2 - YAML parsing
- numpy 2.3.2 - Numerical computing
- typing-extensions 4.15.0 - Type hints extensions
- typing-inspect 0.9.0 - Type hint introspection

**Monitoring & Observability:**
- langsmith 0.4.20 - LangChain tracing and debugging

## Configuration

**Environment:**
- Configuration via `.env` file (example provided in `.env.example`)
- Required variables:
  - `GOOGLE_API_KEY` - Google Generative AI API key
  - `GOOGLE_EMBEDDING_MODEL` - Google embedding model identifier (default: models/embedding-001)
  - `OPENAI_API_KEY` - OpenAI API key
  - `OPENAI_EMBEDDING_MODEL` - OpenAI embedding model (default: text-embedding-3-small)
  - `DATABASE_URL` - PostgreSQL connection string
  - `PG_VECTOR_COLLECTION_NAME` - Vector collection name in PostgreSQL
  - `PDF_PATH` - Path to PDF document for ingestion

**Build:**
- Docker Compose for local development environment
- docker-compose.yml defines PostgreSQL with pgvector extension

## Platform Requirements

**Development:**
- Docker and Docker Compose (for local database setup)
- Python 3.9+ (based on dependency compatibility)
- PostgreSQL 17 (via Docker image: pgvector/pgvector:pg17)

**Production:**
- Python 3.9+ runtime
- PostgreSQL 15+ with pgvector extension
- API access to Google Generative AI and/or OpenAI services
- Network access to external LLM providers

---

*Stack analysis: 2026-03-08*
