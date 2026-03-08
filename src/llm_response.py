"""
LLM response generation module with context-only template enforcement.

This module provides utilities for:
- Formatting prompts with strict context-only instructions
- Calling LLM providers (OpenAI or Google) with template enforcement
- Generating context-aware responses that reject out-of-scope questions
"""

import logging
from typing import Optional
from src.config import load_config, get_active_provider
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System prompt template that enforces context-only responses
SYSTEM_PROMPT_TEMPLATE = """Você é um assistente especializado em consultar documentos PDF.

INSTRUÇÃO CRÍTICA: Responda APENAS com base no contexto fornecido abaixo.
Se a pergunta não pode ser respondida com o contexto, responda EXATAMENTE com:
"Não tenho informações necessárias para responder sua pergunta."

CONTEXTO:
{context}

PERGUNTA: {question}"""


def generate_response(question: str, context: str, provider: str) -> str:
    """
    Generate LLM response using the context-only template.

    Formats the prompt with the question and retrieved context, then calls the
    specified LLM provider (OpenAI or Google) to generate a response.

    Args:
        question: The user's question
        context: The retrieved context from semantic search (can be empty for out-of-scope)
        provider: Either "openai" or "google" to specify which LLM provider to use

    Returns:
        The LLM's generated response as a string

    Raises:
        ValueError: If question is empty, provider is invalid, or LLM call fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if provider not in ("openai", "google"):
        raise ValueError(f'Invalid provider: "{provider}". Must be "openai" or "google".')

    try:
        config = load_config()

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

        # Create LLM instance based on provider
        if provider == "openai":
            # Create OpenAI chat model
            openai_kwargs = {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500,
                "api_key": config["OPENAI_API_KEY"],
            }
            if config.get("OPENAI_BASE_URL"):
                openai_kwargs["base_url"] = config["OPENAI_BASE_URL"]

            llm = ChatOpenAI(**openai_kwargs)
        else:  # provider == "google"
            # Create Google chat model
            google_kwargs = {
                "model": config.get("GOOGLE_LLM_MODEL", "gemini-pro"),
                "temperature": 0.7,
                "max_output_tokens": 500,
                "google_api_key": config["GOOGLE_API_KEY"],
            }
            llm = ChatGoogleGenerativeAI(**google_kwargs)

        logger.info(f"Calling {provider} LLM with prompt (question length: {len(question)})")

        # Call LLM with the formatted prompt
        response = llm.invoke(prompt)

        # Extract text from response
        if hasattr(response, "content"):
            response_text = response.content
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)

        if not response_text or not response_text.strip():
            raise ValueError("LLM returned empty response")

        logger.info(f"✓ Generated response ({len(response_text)} characters)")
        return response_text.strip()

    except Exception as e:
        error_msg = f"Error generating response with {provider} LLM: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def orchestrate_response(question: str, context: str, provider: str) -> str:
    """
    Wrapper function for consistent response generation interface.

    Orchestrates the complete response generation process for consistency
    with the retrieval module's orchestrate_search() pattern.

    Args:
        question: The user's question
        context: The retrieved context from semantic search
        provider: Either "openai" or "google"

    Returns:
        The final response to display to the user

    Raises:
        ValueError: If any parameter is invalid or generation fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if provider not in ("openai", "google"):
        raise ValueError(f'Invalid provider: "{provider}". Must be "openai" or "google".')

    try:
        logger.info("Starting response generation orchestration")

        # Call generate_response with the provided context
        response = generate_response(question, context, provider)

        logger.info("✓ Response generation orchestration completed")
        return response

    except Exception as e:
        error_msg = f"Error in response orchestration: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
