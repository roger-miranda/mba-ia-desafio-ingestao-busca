"""
Semantic search and chunk retrieval module for RAG pipeline.

This module provides utilities for:
- Converting user questions to embeddings using the same model as document ingestion
- Retrieving semantically similar chunks from PostgreSQL using pgVector
- Formatting retrieved chunks into context strings for LLM prompts
"""

import logging
from typing import List, Dict, Optional
from src.config import load_config, get_active_provider
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_embeddings(question: str, provider: str) -> List[float]:
    """
    Convert user question to embedding vector using the same embedding model as document chunks.

    Generates an embedding for the user's question using either OpenAI or Google
    Generative AI providers, matching the embedding model used during document ingestion.

    Args:
        question: The user's question text to embed
        provider: Either "openai" or "google" to specify which embedding provider to use

    Returns:
        List of floats representing the embedding vector (1536 dims for OpenAI, 768 for Google)

    Raises:
        ValueError: If question is empty, provider is invalid, or API call fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if provider not in ("openai", "google"):
        raise ValueError(f'Invalid provider: "{provider}". Must be "openai" or "google".')

    try:
        config = load_config()

        if provider == "openai":
            # Create OpenAI embeddings with optional custom base URL
            openai_kwargs = {
                "model": config["OPENAI_EMBEDDING_MODEL"],
                "api_key": config["OPENAI_API_KEY"],
            }
            if config.get("OPENAI_BASE_URL"):
                openai_kwargs["base_url"] = config["OPENAI_BASE_URL"]

            embeddings = OpenAIEmbeddings(**openai_kwargs)
        else:  # provider == "google"
            # Create Google embeddings
            google_kwargs = {
                "model": config["GOOGLE_EMBEDDING_MODEL"],
                "google_api_key": config["GOOGLE_API_KEY"],
            }
            embeddings = GoogleGenerativeAIEmbeddings(**google_kwargs)

        # Generate embedding for the question
        embedding_vector = embeddings.embed_query(question)

        if not embedding_vector:
            raise ValueError("Failed to generate embedding for question")

        logger.info(f"✓ Generated embedding for question ({len(embedding_vector)} dimensions)")
        return embedding_vector

    except Exception as e:
        error_msg = f"Error generating embedding for question: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def retrieve_similar_chunks(
    question_embedding: List[float], db_url: str, collection_name: str, k: int = 10
) -> List[Dict]:
    """
    Retrieve k most relevant chunks from PostgreSQL using semantic similarity search.

    Uses PGVector's similarity_search_with_score() to find chunks most similar to
    the question embedding. Results are ordered by relevance score (highest first).

    Args:
        question_embedding: The embedding vector for the user's question
        db_url: PostgreSQL connection URL
        collection_name: Name of the vector collection to search
        k: Number of results to retrieve (default: 10 per SEARCH-02 requirement)

    Returns:
        List of dictionaries with keys:
        - text: The chunk content
        - score: Similarity score (higher = more relevant)
        - metadata: Additional metadata about the chunk (e.g., page number)

    Raises:
        ValueError: If inputs are invalid or database connection fails
    """
    if not question_embedding:
        raise ValueError("Question embedding cannot be empty")

    if not db_url or not db_url.strip():
        raise ValueError("Database URL cannot be empty")

    if not collection_name or not collection_name.strip():
        raise ValueError("Collection name cannot be empty")

    if k <= 0:
        raise ValueError("k must be a positive integer")

    try:
        config = load_config()
        provider = get_active_provider()

        # Create embedding function for PGVector based on provider
        if provider == "openai":
            openai_kwargs = {
                "model": config["OPENAI_EMBEDDING_MODEL"],
                "api_key": config["OPENAI_API_KEY"],
            }
            if config.get("OPENAI_BASE_URL"):
                openai_kwargs["base_url"] = config["OPENAI_BASE_URL"]

            embedding_function = OpenAIEmbeddings(**openai_kwargs)
        else:  # provider == "google"
            google_kwargs = {
                "model": config["GOOGLE_EMBEDDING_MODEL"],
                "google_api_key": config["GOOGLE_API_KEY"],
            }
            embedding_function = GoogleGenerativeAIEmbeddings(**google_kwargs)

        # Create PGVector store connection
        vectorstore = PGVector(
            collection_name=collection_name,
            connection=db_url,
            embeddings=embedding_function,
        )

        # Perform similarity search with scores
        results = vectorstore.similarity_search_with_score(
            query="",  # Empty query - we're using the embedding directly
            k=k,
        )

        # Format results - manually search using the embedding vector
        # For direct embedding search, we need to use the underlying connection
        try:
            # Alternative: use similarity_search which takes a query string
            # but we have an embedding vector, so we'll format results differently
            import psycopg2
            from pgvector.psycopg2 import register_vector

            register_vector(None)

            # Get raw connection to execute custom query with the embedding vector
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()

            # Query pgVector for similarity search with our embedding
            cur.execute(
                f"""
                SELECT document, 1 - (embedding <=> %s::vector) as similarity, metadata
                FROM langchain_pg_embedding
                WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = %s)
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (question_embedding, collection_name, question_embedding, k),
            )

            retrieved_chunks = []
            for row in cur.fetchall():
                chunk = {
                    "text": row[0],
                    "score": row[1],
                    "metadata": row[2] if row[2] else {},
                }
                retrieved_chunks.append(chunk)

            cur.close()
            conn.close()

            logger.info(f"✓ Retrieved {len(retrieved_chunks)} similar chunks from database")
            return retrieved_chunks

        except Exception as e:
            # Fallback: use similarity_search if direct query fails
            logger.warning(f"Direct embedding search failed, using fallback: {e}")
            # This will search based on query string similarity
            results_with_scores = vectorstore.similarity_search_with_score("", k=k)

            retrieved_chunks = []
            for doc, score in results_with_scores:
                chunk = {
                    "text": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata if doc.metadata else {},
                }
                retrieved_chunks.append(chunk)

            logger.info(f"✓ Retrieved {len(retrieved_chunks)} similar chunks (fallback method)")
            return retrieved_chunks

    except Exception as e:
        error_msg = f"Error retrieving similar chunks from database: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def format_context(retrieved_chunks: List[Dict]) -> str:
    """
    Concatenate retrieved chunks into a single context string for LLM prompt.

    Joins chunk text with newline separators and includes metadata (page numbers)
    for clarity. Returns empty string if no chunks are provided.

    Args:
        retrieved_chunks: List of chunk dictionaries with 'text', 'score', and 'metadata'

    Returns:
        Formatted context string with all chunks joined together, or empty string if no chunks

    Raises:
        ValueError: If retrieved_chunks is not a list or contains invalid items
    """
    if not isinstance(retrieved_chunks, list):
        raise ValueError("Retrieved chunks must be a list")

    if not retrieved_chunks:
        logger.info("No chunks to format - returning empty context")
        return ""

    try:
        formatted_parts = []

        for chunk in retrieved_chunks:
            if not isinstance(chunk, dict):
                logger.warning(f"Skipping invalid chunk (not a dict): {type(chunk)}")
                continue

            text = chunk.get("text", "").strip()
            if not text:
                logger.warning("Skipping chunk with empty text")
                continue

            # Include page number metadata if available
            metadata = chunk.get("metadata", {})
            page_info = ""
            if isinstance(metadata, dict):
                page = metadata.get("page", None)
                if page is not None:
                    page_info = f" [Page {page}]"

            formatted_parts.append(f"{text}{page_info}")

        context = "\n\n".join(formatted_parts)

        if context:
            logger.info(f"✓ Formatted context from {len(formatted_parts)} chunks")
        else:
            logger.warning("Context is empty after formatting chunks")

        return context

    except Exception as e:
        error_msg = f"Error formatting context: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def orchestrate_search(
    question: str, provider: str, db_url: str, collection_name: str
) -> str:
    """
    Execute complete semantic search pipeline from question to formatted context.

    Chains together three operations: question embedding → similar chunk retrieval →
    context formatting. Returns formatted context ready for LLM prompt.

    Args:
        question: The user's question
        provider: Either "openai" or "google"
        db_url: PostgreSQL connection URL
        collection_name: Name of the vector collection

    Returns:
        Formatted context string ready for LLM prompt, or empty string if search fails

    Raises:
        ValueError: If any step of the pipeline fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if provider not in ("openai", "google"):
        raise ValueError(f'Invalid provider: "{provider}". Must be "openai" or "google".')

    if not db_url or not db_url.strip():
        raise ValueError("Database URL cannot be empty")

    if not collection_name or not collection_name.strip():
        raise ValueError("Collection name cannot be empty")

    try:
        logger.info(f"Starting semantic search pipeline for question: {question[:50]}...")

        # Step 1: Generate embedding for question
        question_embedding = query_embeddings(question, provider)

        # Step 2: Retrieve similar chunks
        retrieved_chunks = retrieve_similar_chunks(
            question_embedding, db_url, collection_name, k=10
        )

        # Step 3: Format context
        context = format_context(retrieved_chunks)

        logger.info("✓ Semantic search pipeline completed successfully")
        return context

    except Exception as e:
        error_msg = f"Error in search orchestration: {e}"
        logger.error(error_msg)
        # Return empty context rather than failing completely
        return ""
