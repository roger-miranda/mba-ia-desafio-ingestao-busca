# Sistema RAG para Consulta de Documentos PDF

## Overview

**Sistema RAG para Consulta de Documentos PDF** is a Retrieval-Augmented Generation (RAG) system that enables intelligent question-answering based exclusively on PDF document content. The system combines semantic search with large language models to provide accurate, contextually-grounded responses without hallucinations or external knowledge injection.

**Core Value Proposition:** Answers based exclusively on PDF content without hallucinations or external knowledge. Every response is grounded in the document with clear traceability to source material.

**Key Capabilities:**
- Semantic search using embeddings to find relevant document sections
- Context-aware question answering with LLM generation
- Support for multiple LLM providers (OpenAI and Google Generative AI)
- Vector storage with PostgreSQL + pgVector for efficient similarity search
- Production-ready error handling and graceful degradation

**Technology Stack:** Python, LangChain, PostgreSQL + pgVector, Docker & Docker Compose, OpenAI/Google APIs

---

## Prerequisites

Before installation, ensure you have the following:

- **Python 3.8 or later** (test with `python --version`)
- **Docker and Docker Compose** (required for PostgreSQL + pgVector container)
- **API keys (at least one):**
  - OpenAI API key (OPENAI_API_KEY) — for GPT-3.5-turbo model, OR
  - Google Generative AI API key (GOOGLE_API_KEY) — for Gemini model
  - (You may provide both; system will default to OpenAI if both present)
- **Disk space:** Minimum 500MB for PostgreSQL, embeddings cache, and indexes
- **PDF document:** Place your document at project root as `document.pdf`

---

## Installation

Follow these step-by-step instructions to set up the project:

**Step 1: Clone or extract the project**
```bash
# If cloning from a repository:
git clone <repository-url>
cd mba-ia-desafio-ingestao-busca

# Or extract from a downloaded archive and navigate to the directory
cd mba-ia-desafio-ingestao-busca
```

**Step 2: Create Python virtual environment**
```bash
python -m venv venv
```

**Step 3: Activate virtual environment**

On Linux/macOS:
```bash
source venv/bin/activate
```

On Windows (Command Prompt):
```bash
venv\Scripts\activate.bat
```

On Windows (PowerShell):
```bash
venv\Scripts\Activate.ps1
```

**Step 4: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Copy and configure environment**
```bash
# Copy the template environment file
cp .env.example .env

# Edit .env with your favorite editor and add API keys
# Linux/macOS:
nano .env

# Or use your preferred editor (VS Code, vim, etc.)
```

**Step 6: Add API keys to .env**

Edit the `.env` file and replace placeholders with your actual keys:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
# OR (at least one API key is required)
GOOGLE_API_KEY=your-actual-google-api-key

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag_db
COLLECTION_NAME=pdf_documents
PDF_PATH=document.pdf
```

---

## Environment Setup

### Start PostgreSQL with pgVector

The system uses PostgreSQL with pgVector extension for efficient semantic search. Docker handles the entire setup automatically.

**Start the database service:**
```bash
docker-compose up -d
```

This command:
- Downloads the PostgreSQL image with pgVector extension
- Creates a PostgreSQL container
- Maps port 5432 to your localhost
- Initializes the `rag_db` database
- Runs in background (detached mode)

**Verify database is running:**
```bash
docker ps | grep postgres
```

You should see output like:
```
CONTAINER_ID  IMAGE                            NAMES
abc123...     ankane/pgvector:latest           postgres_db_1
```

### Environment Variables Explained

The `.env` file contains critical configuration:

| Variable | Example | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI API authentication |
| `GOOGLE_API_KEY` | `AIzaSy...` | Google Generative AI authentication |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/rag_db` | PostgreSQL connection string |
| `COLLECTION_NAME` | `pdf_documents` | Vector collection name in pgVector |
| `PDF_PATH` | `document.pdf` | Path to PDF file (relative or absolute) |

**Important Notes:**
- The system requires **at least one API key** (OpenAI OR Google)
- If both API keys are present, OpenAI is used by default
- The system auto-selects the available provider if only one is configured
- Never commit `.env` to version control (it's in `.gitignore` for security)

---

## Data Ingestion

Before you can ask questions, you must ingest your PDF document into the vector database.

**Step 1: Place PDF in project root**
```bash
# Copy your document to the project root directory
# The file must be named exactly: document.pdf
cp /path/to/your/document.pdf ./document.pdf
```

**Step 2: Run the ingest pipeline**
```bash
python -m src.ingest
```

**What happens during ingestion:**

1. **PDF Loading:** Document is loaded into memory (pages extracted)
2. **Chunking:** Text is split into 1000-character chunks with 150-character overlap for context preservation
3. **Embedding Generation:** Each chunk is converted to a vector embedding using the configured LLM provider's embedding model
4. **Vector Storage:** Embeddings are stored in PostgreSQL pgVector with metadata (chunk index, page number)
5. **Database Indexing:** pgVector creates HNSW index for fast similarity search

**Expected output:**
```
Loading PDF document...
Document loaded: 34 pages
Splitting into chunks...
Created 67 chunks
Generating embeddings...
[████████████████████] 100%
Storing embeddings in PostgreSQL...
✓ Successfully ingested 67 chunks into rag_db
Ready for queries
```

**Time estimate:** 30-60 seconds depending on PDF size and API response time

**Important:** Ingest only needs to run once (unless you update the PDF). Subsequent runs will overwrite the existing vectors.

---

## Running Chat/Usage

Once data ingestion is complete, you can start the interactive chat interface.

**Start the chat CLI:**
```bash
python -m src.chat
```

**Using the chat interface:**

1. System displays prompt: `Pergunta: ` (in Portuguese: "Question: ")
2. Type your question about the document content
3. System responds with `Resposta:` followed by the answer (in Portuguese: "Answer: ")
4. Continue asking questions or type `quit` or `exit` to exit
5. System displays farewell: `Chat encerrado. Obrigado!` (Session ended. Thank you!)

**Example interaction:**
```
Pergunta: Qual é o objetivo principal do documento?
Resposta:
O objetivo principal é descrever a implementação de um sistema RAG...

Pergunta: Quais tecnologias são usadas?
Resposta:
O sistema utiliza Python, LangChain, PostgreSQL com pgVector...

Pergunta: exit
Chat encerrado. Obrigado!
```

**Important usage notes:**
- Use `quit` or `exit` (case-insensitive) to exit gracefully
- Do NOT use Ctrl+C to terminate (use quit/exit commands for clean database shutdown)
- The system accepts questions in both English and Portuguese
- Empty lines are silently ignored
- Each response is generated from context in the PDF only

---

## Example Questions & Expected Answers

Here are example questions you can ask about a typical document. Adjust based on your actual PDF content:

### Question 1: Main Topic
**Q:** "Qual é o tema principal deste documento?" (What is the main topic of this document?)

**Expected Answer Format:**
```
O documento aborda [main topic], com foco em [specific area].
Inclui informações sobre [key subtopic 1] e [key subtopic 2].
```

### Question 2: Specific Detail
**Q:** "Quais são as principais características descritas?" (What are the main characteristics described?)

**Expected Answer Format:**
```
As principais características incluem:
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]
```

### Question 3: Out-of-Scope Question (Rejection Example)
**Q:** "Como posso usar esta informação para gerar renda passiva?" (How can I use this information to generate passive income?)

**Expected Answer Format:**
```
Desculpe, a pergunta está fora do escopo do documento fornecido.
O documento contém informações sobre [actual topic], não sobre [requested topic].
```

### Question 4: Procedural
**Q:** "Quais são os passos para implementar o processo descrito?" (What are the steps to implement the process described?)

**Expected Answer Format:**
```
De acordo com o documento, os passos são:
1. [Step 1 from document]
2. [Step 2 from document]
3. [Step 3 from document]
...
```

### Question 5: Definitions
**Q:** "O que é [term] conforme definido no documento?" (What is [term] as defined in the document?)

**Expected Answer Format:**
```
Segundo o documento, [term] é definido como:
[Definition from document]
```

---

## Architecture Notes

Understanding the system architecture helps troubleshoot issues and extend functionality.

### Three-Stage Pipeline

The system operates through three sequential stages:

```
┌─────────────┐      ┌────────────────┐      ┌──────────────┐
│   Ingest    │  →   │  Semantic      │  →   │  LLM         │
│   Pipeline  │      │  Search        │      │  Generation  │
└─────────────┘      └────────────────┘      └──────────────┘
     ↓                      ↓                       ↓
  PDF → Chunks →     Query Embedding →     Retrieved Context →
  Embeddings       Similarity Search         LLM Template →
  pgVector DB      (k=10 results)           Response
```

### Data Flow Details

1. **Ingest Phase (Once):**
   - PDF document → Text extraction → Chunking (1000 chars, 150 overlap)
   - Embeddings generated via OpenAI or Google API
   - Vectors stored in PostgreSQL pgVector with metadata

2. **Query Phase (Per Question):**
   - User question → Converted to embedding vector
   - pgVector similarity search retrieves top 10 most relevant chunks
   - Chunks concatenated into context string
   - LLM receives context + question through template

3. **Response Phase:**
   - LLM generates response based on context only
   - System rejects out-of-scope questions with specific message
   - Response returned to user with "Resposta:" label

### LLM Provider Support

**OpenAI (Default):**
- Model: gpt-3.5-turbo
- Embedding: text-embedding-ada-002
- Temperature: 0.7 (balances accuracy with variation)
- Max tokens: 1000 (reasonable limit for focused answers)

**Google Generative AI (Fallback):**
- Model: Gemini model
- Embedding: Google's embedding model
- Temperature: 0.7
- Used when OpenAI key unavailable

### Database: PostgreSQL + pgVector

- **Container:** Runs in Docker for isolation and reproducibility
- **Extension:** pgVector for semantic vector search
- **Index:** HNSW index for fast approximate nearest neighbor search
- **Connection:** Pooled connection management via LangChain
- **Collection:** Each run stores vectors under configured collection name

### Context-Only Template

The system uses a strict system prompt that:
- Requires responses to come exclusively from provided context
- Explicitly rejects out-of-scope questions
- Includes clear instructions for handling uncertain answers
- Prevents hallucinations through prompt engineering

---

## Troubleshooting

### Issue: "Connection refused to PostgreSQL"

**Symptom:** Error message like `psycopg2.OperationalError: connection refused` or `could not connect to server`

**Solution:**
1. Verify Docker is running: `docker --version`
2. Check PostgreSQL container is started: `docker-compose up -d`
3. Wait 5-10 seconds for PostgreSQL to initialize (first startup is slower)
4. Verify container is healthy: `docker ps | grep postgres` (should show "postgres" in NAMES)
5. Check database connectivity: `psql postgresql://postgres:postgres@localhost:5432/rag_db -c "SELECT 1"`
6. If still failing, restart the container: `docker-compose restart`

### Issue: "API key invalid" or "Authentication failed"

**Symptom:** Error like `Invalid API key` or `401 Unauthorized`

**Solution:**
1. Verify `.env` file exists in project root: `ls -la .env`
2. Check API key format (no extra spaces or quotes):
   ```bash
   # Open .env and verify:
   OPENAI_API_KEY=sk-xxxxxx  # No spaces around =
   ```
3. For OpenAI: Visit https://platform.openai.com/api-keys to generate/verify key
4. For Google: Visit https://ai.google.dev/tutorials/setup to generate/verify key
5. Test key validity directly (example for OpenAI):
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```
6. Reload terminal environment: `source .env` (though not typically needed with proper setup)

### Issue: "document.pdf not found"

**Symptom:** Error message `FileNotFoundError: document.pdf` or similar

**Solution:**
1. Verify PDF file exists in project root: `ls -la document.pdf`
2. Check file is readable: `file document.pdf` (should show "PDF document")
3. If using different filename, update `PDF_PATH` in `.env`:
   ```bash
   PDF_PATH=my_custom_document.pdf
   ```
4. Ensure path is relative to project root (not absolute path unless necessary)
5. For large PDFs (>100MB), verify disk space: `df -h .`

### Issue: "Questions get rejection response for everything"

**Symptom:** All questions return "Desculpe, a pergunta está fora do escopo..." regardless of content

**Solution:**
1. Verify ingest was completed successfully: Run `python -m src.ingest` again
2. Check PostgreSQL contains data:
   ```bash
   docker exec postgres_db_1 psql -U postgres -d rag_db \
     -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
   ```
   Should return a count > 0
3. Verify vector data is not corrupted:
   ```bash
   python -c "from src.retrieval import retrieve_similar_chunks; \
   chunks = retrieve_similar_chunks('test question'); \
   print(f'Found {len(chunks)} chunks')"
   ```
4. Check embedding model consistency: Ensure same provider (OpenAI or Google) used in both ingest and chat
5. Try ingest with different API key provider:
   ```bash
   # Temporarily swap API keys in .env to test alternate provider
   python -m src.ingest
   ```

### Issue: "Out of memory" or "process killed"

**Symptom:** Process terminates without error message, especially on large PDFs

**Solution:**
1. Increase Docker memory allocation:
   - macOS/Windows: Docker Desktop > Preferences > Resources > Memory: increase to 4GB+
   - Linux: Edit `/etc/docker/daemon.json` to increase memory
2. For very large PDFs, reduce chunk size or overlap in `src/document_processor.py`:
   ```python
   # Reduce chunk size from 1000 to 500
   chunks = text_splitter.split_text(text, chunk_size=500)
   ```
3. Use system memory monitoring: `top` (macOS/Linux) or Task Manager (Windows)

### Issue: "ModuleNotFoundError: No module named 'src'"

**Symptom:** Error when running `python -m src.ingest` or `python -m src.chat`

**Solution:**
1. Verify you're in project root directory: `pwd` should show `.../mba-ia-desafio-ingestao-busca`
2. Verify `src/__init__.py` exists: `ls -la src/__init__.py`
3. Verify virtual environment is activated: Terminal prompt should show `(venv)` prefix
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
5. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`

### Issue: "Slow responses" or "embedding generation takes too long"

**Symptom:** Ingest process hangs or responses take > 30 seconds

**Solution:**
1. Check API rate limits: Review your API provider's rate limit status
2. Verify network connectivity: `ping api.openai.com` or test Google API
3. Check PostgreSQL performance: Ensure vector index created successfully
4. Monitor system resources: `top` or `htop` to check CPU/memory usage
5. Consider batch size: Reduce batch size in `src/document_processor.py` if using Google API
6. Use OpenAI if Google is slow (or vice versa) — swap `GOOGLE_API_KEY` and `OPENAI_API_KEY` priorities

---

## Manual Testing & Consistency Validation

The system includes comprehensive testing tools to validate response accuracy and system performance across different scenarios.

### Unified Test Script

**Location:** `tests/manual/test_validation.py`

A unified script that consolidates all testing capabilities:

**Quick Validation Mode:**
```bash
cd tests/manual
python test_validation.py quick
```
- Tests database connection
- Validates basic search functionality
- Tests 5 random companies
- Fast system health check

**Consistency Test Mode:**
```bash
# Test with different company counts
python test_validation.py consistency 10      # 10 companies (development)
python test_validation.py consistency 100     # 100 companies (default)
python test_validation.py consistency 1000    # 1000 companies (production)
```

**Features:**
- **Comprehensive Testing**: Validates both faturamento (revenue) and ano de fundação (foundation year)
- **Automated Logging**: Saves detailed results to `tests/manual/logs/` with timestamps
- **Performance Metrics**: Tracks response times and success rates
- **Configurable Size**: Test any number of companies via command line parameter
- **Reproducible Results**: Uses fixed seed (42) for consistent testing

**Test Coverage:**
- Database connectivity validation
- Search functionality verification
- Company data accuracy (faturamento + ano)
- Response time performance
- Error handling and edge cases

**Results Interpretation:**
- **≥90%**: 🎉 EXCELENTE! Sistema muito consistente
- **≥75%**: ✅ BOM! Sistema razoavelmente consistente
- **≥50%**: ⚠️ REGULAR. Sistema precisa melhorias
- **<50%**: ❌ CRÍTICO! Sistema inconsistente

**Example Output:**
```
📊 RESULTADOS FINAIS
🎯 Taxa Sucesso Geral: 193/200 (96.5%)
💰 Taxa Sucesso Faturamento: 95/100 (95.0%)
📅 Taxa Sucesso Ano: 98/100 (98.0%)
⏱️ Tempo Médio: 2.5s/pergunta
📄 Log detalhado: logs/teste_consistencia_20260308_160553.txt
```

**Log Files:**
- Automatically saved in `tests/manual/logs/`
- Include detailed per-company test results
- Contain expected vs actual responses
- Timestamp-based naming for easy tracking

---

## Support & Additional Resources

For issues not covered above:
1. Check Python version: `python --version` (should be 3.8+)
2. Review requirements installation: `pip list | grep -E "langchain|openai|google"`
3. Check Docker logs: `docker-compose logs postgres`
4. Enable debug mode: Set `DEBUG=true` in `.env` for verbose output

Project structure reference:
- `src/config.py` — Configuration loading and validation
- `src/document_processor.py` — PDF loading, chunking, embedding
- `src/ingest.py` — Ingest orchestrator (entry point)
- `src/retrieval.py` — Semantic search implementation
- `src/llm_response.py` — LLM integration and template
- `src/search.py` — Search orchestrator combining retrieval + response
- `src/chat.py` — Interactive CLI interface
- `docker-compose.yml` — PostgreSQL + pgVector configuration
- `requirements.txt` — Python package dependencies

---

**Last Updated:** 2026-03-08

For the latest information, check the project repository or documentation.
