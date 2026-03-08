# Requirements: Sistema RAG para Consulta de Documentos PDF

**Defined:** 2026-03-08
**Core Value:** Respostas precisas baseadas exclusivamente no conteúdo do PDF ingerido, sem alucinações ou conhecimento externo

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Ingestão PDF

- [x] **INGEST-01**: Sistema deve carregar PDF do arquivo document.pdf usando PyPDFLoader
- [x] **INGEST-02**: Sistema deve dividir PDF em chunks de 1000 caracteres com overlap de 150 usando RecursiveCharacterTextSplitter
- [x] **INGEST-03**: Sistema deve gerar embeddings para cada chunk usando OpenAI ou Google Generative AI
- [x] **INGEST-04**: Sistema deve armazenar vetores no PostgreSQL com pgVector usando PGVector do LangChain

### CLI e Interface

- [x] **CLI-01**: Sistema deve fornecer interface de chat via linha de comando
- [x] **CLI-02**: Sistema deve aceitar perguntas do usuário em loop interativo
- [x] **CLI-03**: Sistema deve exibir respostas formatadas no terminal
- [x] **CLI-04**: Sistema deve permitir sair do chat de forma limpa

### Busca Vetorial

- [x] **SEARCH-01**: Sistema deve vetorizar pergunta do usuário usando mesmo modelo dos embeddings
- [x] **SEARCH-02**: Sistema deve buscar 10 resultados mais relevantes (k=10) usando similarity_search_with_score
- [x] **SEARCH-03**: Sistema deve concatenar resultados do banco para formar contexto
- [x] **SEARCH-04**: Sistema deve montar prompt específico com contexto recuperado

### LLM e Respostas

- [x] **LLM-01**: Sistema deve usar template de prompt específico fornecido com regras rígidas
- [x] **LLM-02**: Sistema deve chamar LLM (OpenAI ou Google) com prompt montado
- [x] **LLM-03**: Sistema deve retornar resposta baseada apenas no contexto do PDF
- [x] **LLM-04**: Sistema deve rejeitar perguntas fora do contexto com "Não tenho informações necessárias para responder sua pergunta."

### Estrutura e Configuração

- [x] **STRUCT-01**: Sistema deve seguir estrutura obrigatória especificada (src/, requirements.txt, docker-compose.yml, etc.)
- [x] **STRUCT-02**: Sistema deve incluir document.pdf na raiz para ingestão
- [x] **CONFIG-01**: Sistema deve usar configuração via .env para API keys e parâmetros
- [x] **CONFIG-02**: Sistema deve validar variáveis de ambiente necessárias

### Documentação

- [ ] **DOC-01**: README.md deve conter descrição completa sobre como executar e usar o software
- [ ] **DOC-02**: README.md deve incluir comandos de instalação das dependências
- [ ] **DOC-03**: README.md deve incluir comandos de build/setup do ambiente
- [ ] **DOC-04**: README.md deve incluir comandos de execução (ingestão e chat)
- [ ] **DOC-05**: README.md deve incluir exemplos de uso e perguntas

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Interface web/GUI | CLI suficiente para POC |
| Autenticação de usuários | Sistema local sem necessidade |
| Persistência de conversas | Cada pergunta é independente |
| APIs REST | CLI é o objetivo |
| Múltiplos documentos simultâneos | Foco em document.pdf único |
| Processamento de outros formatos | Apenas PDF especificado |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| STRUCT-01 | Phase 1 | Complete (2026-03-08) |
| STRUCT-02 | Phase 1 | Complete (2026-03-08) |
| CONFIG-01 | Phase 1 | Complete (2026-03-08) |
| CONFIG-02 | Phase 1 | Complete (2026-03-08) |
| INGEST-01 | Phase 2 | Complete (2026-03-08) |
| INGEST-02 | Phase 2 | Complete (2026-03-08) |
| INGEST-03 | Phase 2 | Complete (2026-03-08) |
| INGEST-04 | Phase 2 | Complete (2026-03-08) |
| SEARCH-01 | Phase 3 | Complete (2026-03-08) |
| SEARCH-02 | Phase 3 | Complete (2026-03-08) |
| SEARCH-03 | Phase 3 | Complete (2026-03-08) |
| SEARCH-04 | Phase 3 | Complete (2026-03-08) |
| LLM-01 | Phase 3 | Complete (2026-03-08) |
| LLM-02 | Phase 3 | Complete (2026-03-08) |
| LLM-03 | Phase 3 | Complete (2026-03-08) |
| LLM-04 | Phase 3 | Complete (2026-03-08) |
| CLI-01 | Phase 4 | Complete (2026-03-08) |
| CLI-02 | Phase 4 | Complete (2026-03-08) |
| CLI-03 | Phase 4 | Complete (2026-03-08) |
| CLI-04 | Phase 4 | Complete (2026-03-08) |
| DOC-01 | Phase 4 | Pending |
| DOC-02 | Phase 4 | Pending |
| DOC-03 | Phase 4 | Pending |
| DOC-04 | Phase 4 | Pending |
| DOC-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0
- Completed: 20/25 (Phase 1 + Phase 2 + Phase 3 + Phase 4 Plan 1)

---

*Requirements defined: 2026-03-08*
*Last updated: 2026-03-08 after Phase 3 completion*
*Phase 1 requirements (4/4): COMPLETE*
*Phase 2 requirements (4/4): COMPLETE*
*Phase 3 requirements (8/8): COMPLETE*
