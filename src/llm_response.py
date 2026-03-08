"""
LLM response generation module with context-only template enforcement.

This module provides utilities for:
- Formatting prompts with strict context-only instructions
- Calling LLM providers (OpenAI or Google) with template enforcement
- Generating context-aware responses that reject out-of-scope questions
"""

import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System prompt template that enforces context-only responses
SYSTEM_PROMPT_TEMPLATE = """Você é um assistente que responde perguntas com base em dados de empresas de um documento PDF.

IMPORTANTE: Use APENAS as informações do contexto abaixo para responder.
Se a pergunta não puder ser respondida com os dados fornecidos, diga:
"Não tenho informações suficientes para responder sua pergunta."

DADOS DISPONÍVEIS:
{context}

PERGUNTA DO USUÁRIO: {question}

RESPOSTA:"""


def generate_response(question: str, context: str, ai_provider) -> str:
    """
    Generate LLM response using the context-only template.

    Uses the AI provider abstraction to generate responses, ensuring consistency
    across different LLM providers.

    Args:
        question: The user's question
        context: The retrieved context from semantic search (can be empty for out-of-scope)
        ai_provider: AI provider instance to use for response generation

    Returns:
        The LLM's generated response as a string

    Raises:
        ValueError: If question is empty, provider is invalid, or LLM call fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:

        # Format the prompt with question and context
        if not context or not context.strip():
            # For out-of-scope questions, context will be empty
            # The LLM template will instruct it to respond with the rejection message
            prompt = SYSTEM_PROMPT_TEMPLATE.format(
                context="[NO CONTEXT AVAILABLE]",
                question=question
            )
        else:
            prompt = SYSTEM_PROMPT_TEMPLATE.format(
                context=context,
                question=question
            )

        logger.debug(f"Calling {ai_provider.get_provider_name()} LLM "
                    f"({ai_provider.get_llm_model_name()}) with prompt "
                    f"(question length: {len(question)})")

        # Call LLM with the formatted prompt as a system message
        from langchain_core.messages import HumanMessage
        response_text = ai_provider.invoke_llm([HumanMessage(content=prompt)])

        if not response_text or not response_text.strip():
            raise ValueError("LLM returned empty response")

        logger.debug(f"✓ Generated response ({len(response_text)} characters)")
        return response_text.strip()

    except Exception as e:
        error_msg = f"Error generating response with {ai_provider.get_provider_name()} LLM: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def orchestrate_response(question: str, context: str, ai_provider) -> str:
    """
    Wrapper function for consistent response generation interface.

    Orchestrates the complete response generation process for consistency
    with the retrieval module's orchestrate_search() pattern.

    Args:
        question: The user's question
        context: The retrieved context from semantic search
        ai_provider: AI provider instance to use for response generation

    Returns:
        The final response to display to the user

    Raises:
        ValueError: If any parameter is invalid or generation fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:
        logger.debug("Starting response generation orchestration")

        # Call generate_response with the provided context
        response = generate_response(question, context, ai_provider)

        logger.debug("✓ Response generation orchestration completed")
        return response

    except Exception as e:
        error_msg = f"Error in response orchestration: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
