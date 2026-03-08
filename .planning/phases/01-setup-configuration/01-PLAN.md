---
phase: 01-setup-configuration
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .env
  - src/config.py
  - src/__init__.py
autonomous: true
requirements: [STRUCT-01, STRUCT-02, CONFIG-01, CONFIG-02]
user_setup: []
must_haves:
  truths:
    - ".env file exists with all required environment variables"
    - "System validates required API key presence at startup"
    - "Primary/fallback LLM provider system is configurable"
    - "PostgreSQL with pgVector is accessible via docker-compose"
    - "document.pdf exists and is readable from project root"
  artifacts:
    - path: ".env"
      provides: "Environment variable configuration"
      contains: "GOOGLE_API_KEY, OPENAI_API_KEY, DATABASE_URL, others"
    - path: "src/config.py"
      provides: "Environment validation and provider configuration"
      exports: ["load_config", "get_active_provider", "switch_provider"]
    - path: "src/__init__.py"
      provides: "Package initialization with config loading on import"
  key_links:
    - from: "src/__init__.py"
      to: "src/config.py"
      via: "import and call load_config() on startup"
      pattern: "from.*config.*import.*load_config"
    - from: "docker-compose.yml"
      to: "PostgreSQL + pgVector"
      via: "service definition with pgvector/pgvector image"
      pattern: "postgres:.*service_healthy"
---

<objective>
Create environment configuration, variable validation, and LLM provider management system. Ensure all infrastructure is ready for Phase 2 data ingestion.

Purpose: Foundation for runtime configuration and infrastructure health checks.
Output: .env configuration file, config.py module with validation and provider switching, Docker infrastructure verified.
</objective>

<execution_context>
@/Users/rogerio.miranda/.claude/get-shit-done/workflows/execute-plan.md
@/Users/rogerio.miranda/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-setup-configuration/01-CONTEXT.md
@.env.example
@docker-compose.yml
@requirements.txt
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create .env file and environment validation module</name>
  <files>.env, src/config.py</files>
  <action>
    1. Create .env file by copying .env.example and keeping all variable placeholders (no actual API key values needed for this task)

    2. Create src/config.py with the following structure:
       - Function load_config() that:
         * Loads variables from .env using python-dotenv
         * Validates required variables are present: GOOGLE_API_KEY, OPENAI_API_KEY, DATABASE_URL, PG_VECTOR_COLLECTION_NAME, PDF_PATH, GOOGLE_EMBEDDING_MODEL, OPENAI_EMBEDDING_MODEL
         * Raises ValueError with clear message if any required variable is missing, listing which ones
         * Determines primary provider: default to OPENAI if both exist, or whichever is set
         * Returns config dict with all variables and current primary provider
       - Function get_active_provider() that returns which provider is currently primary
       - Function switch_provider(provider_name) that switches between "openai" and "google" providers
         * Sets the other provider as fallback
         * Validates provider_name is either "openai" or "google"
         * Raises ValueError if invalid provider name
       - Global config dict initialized on module load with load_config()

    3. Import behavior: When src/config.py is first imported, it should automatically call load_config() and fail immediately with a clear error if required variables are missing. This ensures early detection of configuration issues.

    Note: Do NOT test if API keys are valid - only check they exist and are non-empty strings.
  </action>
  <verify>
    - File .env exists in project root
    - src/config.py contains load_config(), get_active_provider(), switch_provider() functions
    - Running `python -c "from src.config import load_config; load_config()"` without valid API keys should show clear error listing missing variables
    - Running `python -c "from src.config import get_active_provider; print(get_active_provider())"` returns either "openai" or "google"
  </verify>
  <done>
    .env file created with all required variable placeholders. src/config.py module provides validation, provider detection, and switching. Missing variables trigger clear error messages. Load behavior ensures early detection of configuration issues.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create package initialization with config loading and verify infrastructure</name>
  <files>src/__init__.py</files>
  <action>
    1. Create src/__init__.py that:
       - Imports and calls load_config() at package initialization time
       - Exposes get_active_provider() and switch_provider() for use by other modules
       - Package-level error handling: if config fails to load, print error and exit

    2. Verify infrastructure readiness:
       - Ensure docker-compose.yml exists and contains postgres service with pgvector image (pgvector/pgvector:pg17)
       - Verify postgres service has: correct environment variables (POSTGRES_USER, POSTGRES_DB), healthcheck configured, named volume for persistence, bootstrap_vector_ext service to auto-create vector extension
       - Verify document.pdf exists in project root and is readable (check file size > 0)
       - Document expected DATABASE_URL format in comments: postgresql://postgres:postgres@localhost:5432/rag

    3. This task does NOT start Docker or test database connectivity - only validates file structure and existence. Database connectivity testing happens in Phase 2.
  </action>
  <verify>
    - File src/__init__.py exists and can be imported without errors when .env has valid API keys
    - Running `python -c "import src; from src import get_active_provider, switch_provider"` works
    - docker-compose.yml contains postgres service with pgvector/pgvector:pg17 image
    - Healthcheck in docker-compose.yml tests pg_isready
    - bootstrap_vector_ext service exists and creates vector extension
    - document.pdf exists in project root with file size > 0
  </verify>
  <done>
    src/__init__.py created with auto-loading config and provider functions exposed. Infrastructure files verified: docker-compose.yml structure correct, pgVector extension setup configured, document.pdf present and readable. Project ready for Phase 2 ingestion pipeline.
  </done>
</task>

</tasks>

<verification>
- [ ] .env file exists with all required variable names from .env.example
- [ ] src/config.py implements load_config, get_active_provider, switch_provider
- [ ] src/__init__.py imports config at package initialization
- [ ] Missing API key triggers clear error message
- [ ] Provider switching works (can call switch_provider("google") to swap primary provider)
- [ ] docker-compose.yml has postgres service with pgvector image and healthcheck
- [ ] document.pdf exists in project root and is readable
</verification>

<success_criteria>
1. Environment configuration system is complete: .env file exists, load_config() validates all required variables, missing keys trigger clear errors
2. Provider system allows switching between OpenAI and Google with automatic fallback configuration
3. Docker Compose infrastructure is verified: postgres with pgVector extension, healthcheck, persistence via named volume
4. document.pdf is confirmed to exist in project root
5. Phase 1 requirements met: STRUCT-01 (structure), STRUCT-02 (document.pdf), CONFIG-01 (environment config), CONFIG-02 (validation)
</success_criteria>

<output>
After completion, create `.planning/phases/01-setup-configuration/01-SUMMARY.md` documenting:
- Environment variables configured and validation strategy
- Provider switching implementation details
- Docker Compose infrastructure verification results
- Files created: .env, src/config.py, src/__init__.py
</output>
