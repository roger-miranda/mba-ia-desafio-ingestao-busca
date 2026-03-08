# Sistema RAG para Consulta de Documentos PDF

## What This Is

Um sistema RAG (Retrieval-Augmented Generation) que permite fazer ingestão de arquivos PDF em um banco de dados PostgreSQL com pgVector e realizar consultas via CLI. O sistema responde perguntas baseadas exclusivamente no conteúdo do documento PDF, rejeitando perguntas fora do contexto. É uma prova de conceito usando Python, LangChain e tecnologias vetoriais.

## Core Value

Respostas precisas baseadas exclusivamente no conteúdo do PDF ingerido, sem alucinações ou conhecimento externo.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Python + LangChain framework configurado — existing
- ✓ PostgreSQL com pgVector via Docker Compose — existing
- ✓ Estrutura básica de módulos (ingest.py, search.py, chat.py) — existing
- ✓ Configuração multi-LLM (Google Generative AI e OpenAI) — existing
- ✓ Gerenciamento de dependências com requirements.txt — existing
- ✓ Configuração de ambiente via .env — existing

### Active

<!-- Current scope. Building toward these. -->

- [ ] **PDF-001**: Ingestão de PDF com chunks de 1000 caracteres e overlap de 150
- [ ] **PDF-002**: Conversão de chunks em embeddings e armazenamento no PostgreSQL
- [ ] **CLI-001**: Interface de chat via linha de comando para perguntas do usuário
- [ ] **SEARCH-001**: Busca vetorial com k=10 resultados mais relevantes
- [ ] **LLM-001**: Integração com LLM usando template de prompt específico
- [ ] **RESP-001**: Respostas limitadas ao contexto do PDF com rejeição de perguntas fora do escopo
- [ ] **STRUCT-001**: Estrutura de arquivos conforme especificação (document.pdf na raiz, etc.)

### Out of Scope

- Interface web ou GUI — Apenas CLI necessário para POC
- Múltiplos documentos — Foco em um único document.pdf
- Autenticação de usuários — Sistema local sem necessidade de auth
- Persistência de histórico de conversas — Cada pergunta é independente
- Interfaces de API REST — CLI é suficiente para demonstração

## Context

**Finalidade:** Prova de conceito para demonstração técnica ou acadêmica (MBA)

**Domínio:** Sistema RAG genérico para documentos PDF com foco em precisão de respostas

**Arquitetura existente:**
- Pipeline modular em três estágios: Ingestão → Busca/Retrieval → Chat/Geração
- Suporte a múltiplos provedores de LLM (Google e OpenAI)
- Banco vetorial PostgreSQL com pgVector para busca semântica

**Estado atual:** Infraestrutura e dependências configuradas, mas implementações core são stubs que precisam ser completadas

## Constraints

- **Linguagem**: Python — Requisito obrigatório do projeto
- **Framework**: LangChain — Tecnologia obrigatória especificada
- **Banco de dados**: PostgreSQL + pgVector — Extensão vetorial obrigatória
- **Execução**: Docker & Docker Compose — Para ambiente de desenvolvimento
- **Chunking**: 1000 caracteres com overlap de 150 — Parâmetros específicos
- **Busca**: k=10 resultados por consulta — Limite fixo de contexto
- **Template**: Prompt específico fornecido — Deve ser usado exatamente como especificado

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| LangChain como framework principal | Obrigatório pelo projeto + simplifica integração LLM/vector store | ✓ Good — já configurado e funcionando |
| PostgreSQL + pgVector para vectores | Requisito obrigatório + melhor que soluções cloud para POC local | ✓ Good — setup via Docker funcional |
| Suporte a Google e OpenAI | Flexibilidade para escolher provedor conforme disponibilidade de API keys | — Pending — implementar lógica de seleção |
| Estrutura modular (ingest/search/chat) | Separação clara de responsabilidades facilita desenvolvimento e teste | ✓ Good — arquitetura bem definida |
| Docker Compose para desenvolvimento | Simplifica setup de PostgreSQL + pgVector para desenvolvedores | ✓ Good — funciona bem para ambiente local |

---
*Last updated: 2026-03-08 after project initialization*