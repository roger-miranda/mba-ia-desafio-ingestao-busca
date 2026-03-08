# Coding Conventions

**Analysis Date:** 2026-03-08

## Naming Patterns

**Files:**
- Lowercase with underscores for Python modules: `ingest.py`, `chat.py`, `search.py`

**Functions:**
- Snake_case for function names (Python standard): `ingest_pdf()`, `search_prompt()`, `main()`

**Variables:**
- Snake_case for variable names: `PDF_PATH`, `PROMPT_TEMPLATE`, `chain`
- Constants use UPPERCASE_WITH_UNDERSCORES: `PDF_PATH`, `PROMPT_TEMPLATE`

**Types:**
- No type hints currently used in codebase
- Pydantic is available in dependencies for type validation if needed

## Code Style

**Formatting:**
- No explicit formatter configured (black, autopep8, or similar not in requirements.txt)
- Standard Python indentation appears to be 4 spaces
- Line length convention not specified - varies in current code

**Linting:**
- No linting tool configured (pylint, flake8, or ruff not in requirements.txt)
- No pyproject.toml, setup.cfg, or .pylintrc file present

## Import Organization

**Order:**
1. Standard library imports (os, sys, etc.)
2. Third-party imports (dotenv, langchain, etc.)
3. Local imports (from search import search_prompt)

**Path Aliases:**
- No path aliases or relative imports detected
- All imports use standard module paths

**Current Pattern Example:**
```python
# From src/chat.py
from search import search_prompt

# From src/ingest.py
import os
from dotenv import load_dotenv
```

## Error Handling

**Patterns:**
- Conditional checks before proceeding: `if not chain: print(...); return`
- Print-based error messaging currently in use
- No try/except blocks in current code
- No custom exception handling detected

**Current Pattern Example:**
```python
# From src/chat.py
if not chain:
    print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
    return
```

## Logging

**Framework:** Console printing via `print()` statements

**Patterns:**
- Error messages printed directly to console in Portuguese
- No structured logging library configured
- No log levels (INFO, DEBUG, ERROR) implemented
- Future consideration: `logging` module from stdlib or structured logger via LangChain

## Comments

**When to Comment:**
- Limited comments in current codebase
- Docstrings not present

**JSDoc/TSDoc:**
- Not applicable (Python project, not TypeScript)
- Python docstrings convention not currently followed

## Function Design

**Size:**
- Functions are very small currently (stub implementations)
- `ingest_pdf()`: Single pass statement (1 line)
- `search_prompt()`: Single pass statement (1 line)
- `main()`: 5 lines with check + pass

**Parameters:**
- Optional parameters used: `search_prompt(question=None)`
- Minimal parameter passing in current code

**Return Values:**
- Implicit returns (None) for stub functions
- No explicit return type annotations

## Module Design

**Exports:**
- Entry point functions: `ingest_pdf()`, `main()`, `search_prompt()`
- Prompt template exposed as module-level constant: `PROMPT_TEMPLATE`
- Conditional `if __name__ == "__main__":` pattern used for executable modules

**Barrel Files:**
- Not used - no __init__.py files in src directory
- Flat module structure: `src/ingest.py`, `src/chat.py`, `src/search.py`

## Environment Configuration

**Pattern:**
- `.env` file loading via python-dotenv: `from dotenv import load_dotenv; load_dotenv()`
- Environment variables accessed via `os.getenv()`: `PDF_PATH = os.getenv("PDF_PATH")`
- `.env.example` file provided with required keys: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `PDF_PATH`, etc.

**Current Environment Variables:**
- `PDF_PATH`: Path to PDF file for ingestion
- `GOOGLE_API_KEY`: Google AI API credentials
- `GOOGLE_EMBEDDING_MODEL`: Embedding model identifier
- `OPENAI_API_KEY`: OpenAI API credentials
- `OPENAI_EMBEDDING_MODEL`: OpenAI embedding model identifier
- `DATABASE_URL`: PostgreSQL database connection string
- `PG_VECTOR_COLLECTION_NAME`: Vector store collection identifier

---

*Convention analysis: 2026-03-08*
