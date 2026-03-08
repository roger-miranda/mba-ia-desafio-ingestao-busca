
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
    Execute the complete search and response pipeline using the local PROMPT_TEMPLATE.

    This function:
    1. Performs semantic search to retrieve relevant chunks
    2. Uses the PROMPT_TEMPLATE defined in this module to generate responses
    3. Ensures consistent rejection message for out-of-scope questions

    Args:
        user_question: The user's question to process
        ai_provider_instance: AI provider instance to use (optional, creates one if None)

    Returns:
        The final response text to display to the user
    """
    from src.retrieval import orchestrate_search
    from src.config import load_config
    from src.providers import get_ai_provider
    from langchain_core.messages import HumanMessage
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

        # Step 2: Format prompt using the template defined in this module
        if not search_results or not search_results.strip():
            context = "[NO CONTEXT AVAILABLE]"
        else:
            context = search_results

        prompt = PROMPT_TEMPLATE.format(
            contexto=context,
            pergunta=user_question
        )

        # Step 3: Generate response using the AI provider directly
        response = ai_provider_instance.invoke_llm([HumanMessage(content=prompt)])

        if not response or not response.strip():
            return "Não tenho informações necessárias para responder sua pergunta."

        return response.strip()

    except Exception as e:
        logger.error(f"Error in search_prompt orchestration: {e}")
        # Return user-friendly error message
        return "Não tenho informações necessárias para responder sua pergunta."