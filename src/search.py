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

def search_prompt(user_question: str, ai_provider_instance=None) -> str:
    """
    Execute the complete search and response pipeline.

    This function bridges the retrieval and LLM generation layers by orchestrating:
    1. Semantic search to retrieve relevant chunks
    2. LLM response generation based on retrieved context

    Args:
        user_question: The user's question to process
        ai_provider_instance: AI provider instance to use (optional, creates one if None)

    Returns:
        The final response text to display to the user
    """
    from src.retrieval import orchestrate_search
    from src.llm_response import orchestrate_response
    from src.config import load_config
    from src.providers import get_ai_provider
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Load configuration to get database settings
        config = load_config()
        db_url = config.get("DATABASE_URL")
        collection_name = config.get("PG_VECTOR_COLLECTION_NAME")

        # Use provided provider instance or create one silently (without logs)
        if ai_provider_instance is None:
            ai_provider_instance = get_ai_provider(None, config, use_fallback=True, log_selection=False)

        # Step 1: Retrieve relevant chunks from vector database
        search_results = orchestrate_search(
            question=user_question,
            ai_provider=ai_provider_instance,
            db_url=db_url,
            collection_name=collection_name
        )

        # Step 2: Generate response from retrieved context
        response = orchestrate_response(
            question=user_question,
            context=search_results,
            ai_provider=ai_provider_instance
        )

        return response

    except Exception as e:
        logger.error(f"Error in search_prompt orchestration: {e}")
        # Return user-friendly error message
        return f"Não tenho informações necessárias para responder sua pergunta."