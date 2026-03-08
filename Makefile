# Makefile for RAG PDF System
# Sistema RAG para Consulta de Documentos PDF

# Variables
PYTHON := python
PIP := pip
VENV_DIR := venv
DOCKER_COMPOSE := docker-compose
SRC_DIR := src
TESTS_DIR := tests

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

##@ Environment Setup

.PHONY: setup
setup: venv install-deps setup-env ## Complete initial setup (venv + dependencies + .env)
	@echo "$(GREEN)✓ Setup completo! Próximos passos:$(NC)"
	@echo "  1. Configure suas API keys em .env"
	@echo "  2. Execute: make start-db"
	@echo "  3. Execute: make ingest"
	@echo "  4. Execute: make chat"

.PHONY: venv
venv: ## Create Python virtual environment
	@echo "$(BLUE)Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✓ Virtual environment criado em $(VENV_DIR)$(NC)"
	@echo "$(YELLOW)Ative com: source $(VENV_DIR)/bin/activate$(NC)"

.PHONY: install-deps
install-deps: ## Install Python dependencies
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)❌ Virtual environment não encontrado. Execute: make venv$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Instalando dependências...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"

.PHONY: setup-env
setup-env: ## Copy .env.example to .env if not exists
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Criando arquivo .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️ Configure suas API keys em .env$(NC)"; \
	else \
		echo "$(GREEN)✓ Arquivo .env já existe$(NC)"; \
	fi

.PHONY: clean-env
clean-env: ## Remove virtual environment
	@echo "$(YELLOW)Removendo ambiente virtual...$(NC)"
	rm -rf $(VENV_DIR)
	@echo "$(GREEN)✓ Virtual environment removido$(NC)"

##@ Database Operations

.PHONY: start-db
start-db: ## Start PostgreSQL with pgVector using Docker
	@echo "$(BLUE)Iniciando PostgreSQL + pgVector...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Banco de dados iniciado$(NC)"
	@echo "$(YELLOW)Aguarde ~10s para inicialização completa$(NC)"

.PHONY: stop-db
stop-db: ## Stop PostgreSQL container
	@echo "$(BLUE)Parando PostgreSQL...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Banco de dados parado$(NC)"

.PHONY: restart-db
restart-db: ## Restart PostgreSQL container
	@echo "$(BLUE)Reiniciando PostgreSQL...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Banco de dados reiniciado$(NC)"

.PHONY: db-status
db-status: ## Check database container status
	@echo "$(BLUE)Status do banco de dados:$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)Logs recentes:$(NC)"
	@$(DOCKER_COMPOSE) logs --tail=10 postgres

.PHONY: db-clean
db-clean: ## Remove database container and volumes (DESTRUCTIVE)
	@echo "$(RED)⚠️ ATENÇÃO: Isso removerá TODOS os dados do banco!$(NC)"
	@read -p "Tem certeza? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(DOCKER_COMPOSE) down -v; \
		echo "$(GREEN)✓ Banco de dados e volumes removidos$(NC)"; \
	else \
		echo "$(YELLOW)Operação cancelada$(NC)"; \
	fi

##@ Application Operations

.PHONY: ingest
ingest: check-venv check-db ## Run PDF ingestion pipeline
	@echo "$(BLUE)Executando ingestão de documentos...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m $(SRC_DIR).ingest
	@echo "$(GREEN)✓ Ingestão concluída$(NC)"

.PHONY: chat
chat: check-venv check-db ## Start interactive chat interface
	@echo "$(BLUE)Iniciando chat interativo...$(NC)"
	@echo "$(YELLOW)Use 'exit' ou 'quit' para sair$(NC)"
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m $(SRC_DIR).chat

.PHONY: quick-start
quick-start: setup start-db ingest ## Complete quick start (setup + db + ingest)
	@echo "$(GREEN)🚀 Sistema pronto! Execute 'make chat' para começar$(NC)"

##@ Testing Operations

.PHONY: test-quick
test-quick: check-venv ## Run quick validation test (5 companies)
	@echo "$(BLUE)Executando teste rápido de validação...$(NC)"
	cd $(TESTS_DIR)/manual && \
	../../$(VENV_DIR)/bin/python test_validation.py quick

.PHONY: test-consistency
test-consistency: check-venv ## Run consistency test (100 companies)
	@echo "$(BLUE)Executando teste de consistência...$(NC)"
	cd $(TESTS_DIR)/manual && \
	../../$(VENV_DIR)/bin/python test_validation.py consistency 100

.PHONY: test-consistency-small
test-consistency-small: check-venv ## Run small consistency test (10 companies)
	@echo "$(BLUE)Executando teste de consistência pequeno...$(NC)"
	cd $(TESTS_DIR)/manual && \
	../../$(VENV_DIR)/bin/python test_validation.py consistency 10

.PHONY: test-consistency-large
test-consistency-large: check-venv ## Run large consistency test (1000 companies)
	@echo "$(BLUE)Executando teste de consistência grande...$(NC)"
	cd $(TESTS_DIR)/manual && \
	../../$(VENV_DIR)/bin/python test_validation.py consistency 1000

.PHONY: test-logs
test-logs: ## Show recent test logs
	@echo "$(BLUE)Logs de teste mais recentes:$(NC)"
	@ls -lt $(TESTS_DIR)/manual/logs/ | head -5
	@echo ""
	@echo "$(BLUE)Para ver um log específico:$(NC)"
	@echo "  cat $(TESTS_DIR)/manual/logs/[nome_do_arquivo]"

##@ Development & Maintenance
.PHONY: clean-cache
clean-cache: ## Remove Python cache files
	@echo "$(BLUE)Limpando cache Python...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cache limpo$(NC)"

.PHONY: clean-logs
clean-logs: ## Remove test logs
	@echo "$(YELLOW)Removendo logs de teste...$(NC)"
	rm -f $(TESTS_DIR)/manual/logs/*.txt
	@echo "$(GREEN)✓ Logs removidos$(NC)"

.PHONY: clean-all
clean-all: clean-cache clean-logs stop-db clean-env ## Clean everything (cache, logs, db, venv)
	@echo "$(GREEN)✓ Limpeza completa concluída$(NC)"

##@ Information & Help

.PHONY: status
status: ## Show system status
	@echo "$(BLUE)=== Status do Sistema RAG ===$(NC)"
	@echo ""
	@echo "$(BLUE)Virtual Environment:$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(GREEN)✓ Criado$(NC)"; \
	else \
		echo "$(RED)❌ Não encontrado - execute 'make venv'$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)Arquivo .env:$(NC)"
	@if [ -f .env ]; then \
		echo "$(GREEN)✓ Existe$(NC)"; \
	else \
		echo "$(RED)❌ Não encontrado - execute 'make setup-env'$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)Banco de dados:$(NC)"
	@if $(DOCKER_COMPOSE) ps | grep -q postgres; then \
		echo "$(GREEN)✓ Rodando$(NC)"; \
	else \
		echo "$(RED)❌ Parado - execute 'make start-db'$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)Documento PDF:$(NC)"
	@if [ -f document.pdf ]; then \
		echo "$(GREEN)✓ Encontrado (document.pdf)$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ document.pdf não encontrado$(NC)"; \
	fi

.PHONY: requirements
requirements: ## Show system requirements
	@echo "$(BLUE)=== Requisitos do Sistema ===$(NC)"
	@echo "Python: $(shell python --version 2>/dev/null || echo 'Não encontrado')"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Não encontrado')"
	@echo "Docker Compose: $(shell docker-compose --version 2>/dev/null || echo 'Não encontrado')"
	@echo ""
	@echo "$(BLUE)Checklist:$(NC)"
	@echo "□ Python 3.8+"
	@echo "□ Docker instalado"
	@echo "□ Docker Compose instalado"
	@echo "□ API key (OpenAI ou Google)"
	@echo "□ Arquivo document.pdf no root"

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Sistema RAG para Consulta de Documentos PDF$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Uso: make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Início rápido:$(NC)"
	@echo "  1. make setup          # Setup inicial completo"
	@echo "  2. Configure API keys em .env"
	@echo "  3. make quick-start    # Inicia tudo"
	@echo "  4. make chat           # Interface de chat"

##@ Internal Helpers (não execute diretamente)

.PHONY: check-venv
check-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)❌ Virtual environment não encontrado$(NC)"; \
		echo "Execute: make venv"; \
		exit 1; \
	fi

.PHONY: check-db
check-db:
	@if ! $(DOCKER_COMPOSE) ps | grep -q postgres; then \
		echo "$(RED)❌ Banco de dados não está rodando$(NC)"; \
		echo "Execute: make start-db"; \
		exit 1; \
	fi

# Phony targets
.PHONY: all clean install test