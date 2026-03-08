PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
    """
    Orchestrator function that returns a callable chain for search and response.

    This function bridges the retrieval and LLM generation layers, returning a
    callable that accepts a question and returns a response text by orchestrating:
    1. Semantic search to retrieve relevant chunks
    2. LLM response generation based on retrieved context

    Args:
        question: Optional question for testing (not used in normal flow)

    Returns:
        A callable function that takes (question) and returns (response_text)
    """
    from src.retrieval import orchestrate_search
    from src.llm_response import orchestrate_response
    from src.config import load_config, get_active_provider
    import logging

    logger = logging.getLogger(__name__)

    def search_and_respond(user_question: str) -> str:
        """
        Inner function that executes the complete search and response pipeline.

        Args:
            user_question: The user's question to process

        Returns:
            The final response text to display to the user
        """
        try:
            # Load configuration to get database and provider settings
            config = load_config()
            provider = get_active_provider()
            db_url = config.get("DATABASE_URL")
            collection_name = config.get("PG_VECTOR_COLLECTION_NAME")

            # Step 1: Retrieve relevant chunks from vector database
            search_results = orchestrate_search(
                question=user_question,
                provider=provider,
                db_url=db_url,
                collection_name=collection_name
            )

            # Step 2: Generate response from retrieved context
            response = orchestrate_response(
                question=user_question,
                context=search_results,
                provider=provider
            )

            return response

        except Exception as e:
            logger.error(f"Error in search_prompt orchestration: {e}")
            # Return user-friendly error message
            return f"Não tenho informações necessárias para responder sua pergunta."

    return search_and_respond