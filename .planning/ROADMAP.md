# ROADMAP: Sistema RAG para Consulta de Documentos PDF

**Project:** Sistema RAG (Retrieval-Augmented Generation)
**Created:** 2026-03-08
**Depth:** Quick (4 phases)
**Coverage:** 25/25 v1 requirements mapped

---

## Phases

- [x] **Phase 1: Setup & Configuration** - Foundation infrastructure and environment validation (COMPLETE)
- [x] **Phase 2: Data Ingestion Pipeline** - PDF loading, chunking, embedding, and vector storage (COMPLETE)
- [x] **Phase 3: Retrieval & Generation Pipeline** - Semantic search and LLM-powered response generation (COMPLETE)
- [x] **Phase 4: CLI Interface & Documentation** - User interaction layer and complete documentation (COMPLETE - 2/2 plans)

---

## Phase Details

### Phase 1: Setup & Configuration
**Goal:** Environment is properly configured with all dependencies and infrastructure ready for data ingestion

**Depends on:** Nothing (foundation)

**Requirements:** STRUCT-01, STRUCT-02, CONFIG-01, CONFIG-02

**Success Criteria** (what must be TRUE for users):
1. Project structure matches specification with src/, requirements.txt, docker-compose.yml, and .env configured
2. PostgreSQL database with pgVector extension is running and accessible via Docker Compose
3. Environment variables for API keys (OpenAI/Google) and configuration parameters are validated at startup
4. document.pdf is available in project root and ready for ingestion

**Plans:** 1 plan

Plan list:
- [x] 01-PLAN.md — Configure environment variables, validate required config, implement LLM provider switching system (COMPLETE)

---

### Phase 2: Data Ingestion Pipeline
**Goal:** PDF documents are loaded, chunked, vectorized, and persisted in vector database

**Depends on:** Phase 1

**Requirements:** INGEST-01, INGEST-02, INGEST-03, INGEST-04

**Status:** COMPLETE (2026-03-08)

**Success Criteria** (what must be TRUE for users):
1. ✓ User can execute ingest command that reads document.pdf from project root
2. ✓ PDF is split into 1000-character chunks with 150-character overlap using RecursiveCharacterTextSplitter
3. ✓ Each chunk is converted to embeddings using configured LLM provider (OpenAI or Google Generative AI)
4. ✓ Embeddings and chunk text are stored in PostgreSQL with pgVector for semantic search retrieval

**Plans:** 1 plan

Plan list:
- [x] 02-01-PLAN.md — Load PDF, chunk into 1000-char pieces (150-char overlap), generate embeddings, and persist in pgVector (COMPLETE)

---

### Phase 3: Retrieval & Generation Pipeline
**Goal:** User questions are processed and answered with responses based exclusively on PDF content

**Depends on:** Phase 2

**Requirements:** SEARCH-01, SEARCH-02, SEARCH-03, SEARCH-04, LLM-01, LLM-02, LLM-03, LLM-04

**Status:** COMPLETE (2026-03-08)

**Success Criteria** (what must be TRUE for users):
1. ✓ User question is vectorized using the same embedding model that processed the PDF chunks
2. ✓ Top 10 most relevant chunks are retrieved from PostgreSQL using semantic similarity search
3. ✓ Retrieved chunks are concatenated and formatted into context for the LLM prompt
4. ✓ LLM generates response using template that enforces context-only answers without external knowledge
5. ✓ Questions outside document scope are rejected with message "Não tenho informações necessárias para responder sua pergunta."

**Plans:** 1/1 plans complete

Plan list:
- [x] 03-01-PLAN.md — Semantic search retrieval module, LLM response generation with context-only template, integration testing (COMPLETE)

---

### Phase 4: CLI Interface & Documentation
**Goal:** Users can interact with the system via command line and understand how to deploy and use it

**Depends on:** Phase 3

**Requirements:** CLI-01, CLI-02, CLI-03, CLI-04, DOC-01, DOC-02, DOC-03, DOC-04, DOC-05

**Success Criteria** (what must be TRUE for users):
1. User can start interactive CLI chat and repeatedly ask questions in a loop
2. User receives formatted responses displayed clearly in terminal
3. User can cleanly exit chat with 'quit' or 'exit' command without errors
4. README.md contains complete documentation: installation steps, environment setup, Docker Compose commands, ingest execution, chat usage, and example questions

**Plans:** 2 plans

Plan list:
- [x] 04-01-PLAN.md — Implement search_prompt orchestrator and interactive CLI loop (CLI-01 through CLI-04) (COMPLETE)
- [x] 04-02-PLAN.md — Write comprehensive README.md documentation (DOC-01 through DOC-05) (COMPLETE)

---

## Progress Tracking

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Setup & Configuration | 1/1 | COMPLETE | 2026-03-08 |
| 2. Data Ingestion Pipeline | 1/1 | COMPLETE | 2026-03-08 |
| 3. Retrieval & Generation Pipeline | 1/1 | COMPLETE | 2026-03-08 |
| 4. CLI Interface & Documentation | 2/2 | COMPLETE | 2026-03-08 |

**Overall Progress:** 4/4 phases complete (100%)

---

## Coverage Summary

**Total v1 requirements:** 25
**Mapped to phases:** 25
**Unmapped/Orphaned:** 0

### Requirement-to-Phase Mapping

| Category | Requirements | Phase |
|----------|--------------|-------|
| Structure & Config | STRUCT-01, STRUCT-02, CONFIG-01, CONFIG-02 | Phase 1 |
| Ingest | INGEST-01, INGEST-02, INGEST-03, INGEST-04 | Phase 2 |
| Search & LLM | SEARCH-01, SEARCH-02, SEARCH-03, SEARCH-04, LLM-01, LLM-02, LLM-03, LLM-04 | Phase 3 |
| CLI & Documentation | CLI-01, CLI-02, CLI-03, CLI-04, DOC-01, DOC-02, DOC-03, DOC-04, DOC-05 | Phase 4 |

---

*Roadmap created: 2026-03-08*
*Phase 1 completed: 2026-03-08*
*Phase 2 completed: 2026-03-08*
*Phase 3 completed: 2026-03-08*
*Phase 4 Plan 1 completed: 2026-03-08*
*Phase 4 Plan 2 completed: 2026-03-08*
*Overall progress: 100% complete (4 of 4 phases)*
*Project Status: COMPLETE*
