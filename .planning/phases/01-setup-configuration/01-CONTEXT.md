# Phase 1: Setup & Configuration - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Environment configuration and infrastructure setup for a RAG system. Sets up project structure, PostgreSQL with pgVector via Docker, environment variables for API keys (OpenAI/Google), and ensures document.pdf is ready for ingestion.

</domain>

<decisions>
## Implementation Decisions

### Database setup approach
- Use exactly the existing docker-compose.yml file in the project
- Named volumes for data persistence across container restarts
- Auto-install pgVector extension on container startup
- All database credentials and connection config via environment variables (.env file)

### Environment validation strategy
- Fail immediately with clear error message when required environment variables (API keys) are missing
- No API key validation beyond checking presence - don't test if keys actually work
- Primary/fallback provider system: one provider is primary, the other is automatic fallback
- CLI command to switch which provider is primary (the other becomes secondary automatically)
- document.pdf validation: existence check only - just verify file exists in project root

### Claude's Discretion
- Exact error message format and content
- Specific environment variable naming conventions
- Docker compose service naming and configuration details

</decisions>

<specifics>
## Specific Ideas

- "Use exatamente o docker-compose.yml já disponível no projeto" - use existing Docker Compose configuration exactly as provided
- Provider switching behavior: "deve permitir ao usuário, via comando do cli, trocar o provider primário. Neste momento o outro provider se torna o secundário (fallback) automaticamente"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-setup-configuration*
*Context gathered: 2026-03-08*