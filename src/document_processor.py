"""
Document processor module for PDF ingestion and vector storage.

This module provides utilities for:
- Loading PDFs using LangChain's PyPDFLoader
- Chunking documents with configurable size and overlap
- Generating embeddings using OpenAI or Google Generative AI
- Storing embeddings in PostgreSQL with pgVector
"""

from typing import List, Tuple
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector

from src.config import load_config, get_active_provider


def load_pdf_documents(pdf_path: str) -> List[Document]:
    """
    Load PDF documents from a file using PyPDFLoader.

    Args:
        pdf_path: Path to the PDF file to load

    Returns:
        List of Document objects with page_content and metadata

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the PDF cannot be loaded
    """
    try:
        if not pdf_path:
            raise ValueError("PDF path cannot be empty")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            raise ValueError(f"No content loaded from PDF: {pdf_path}")

        return documents
    except FileNotFoundError as e:
        raise FileNotFoundError(f"PDF file not found at {pdf_path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Error loading PDF from {pdf_path}: {e}") from e


def chunk_documents(
    documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 150
) -> List[Document]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.

    Args:
        documents: List of Document objects to chunk
        chunk_size: Size of each chunk in characters (default: 1000)
        chunk_overlap: Overlap between consecutive chunks in characters (default: 150)

    Returns:
        List of chunked Document objects with preserved metadata
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No chunks created from documents")

    return chunks


def generate_embeddings_batch(
    documents: List[Document], provider: str
) -> List[Tuple[str, List[float]]]:
    """
    Generate embeddings for a batch of documents using the specified provider.

    Args:
        documents: List of Document objects to embed
        provider: Either "openai" or "google"

    Returns:
        List of tuples containing (chunk_text, embedding_vector)

    Raises:
        ValueError: If provider is invalid or if embedding generation fails
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")

    if provider not in ("openai", "google"):
        raise ValueError(f'Invalid provider: "{provider}". Must be "openai" or "google".')

    config = load_config()

    try:
        if provider == "openai":
            embeddings = OpenAIEmbeddings(
                model=config["OPENAI_EMBEDDING_MODEL"],
                api_key=config["OPENAI_API_KEY"],
            )
        else:  # provider == "google"
            embeddings = GoogleGenerativeAIEmbeddings(
                model=config["GOOGLE_EMBEDDING_MODEL"],
                google_api_key=config["GOOGLE_API_KEY"],
            )

        # Extract text content from documents
        texts = [doc.page_content for doc in documents]

        # Generate embeddings in batch
        embedding_vectors = embeddings.embed_documents(texts)

        # Pair text with embeddings
        embeddings_data = list(zip(texts, embedding_vectors))

        if not embeddings_data:
            raise ValueError("No embeddings generated")

        return embeddings_data

    except Exception as e:
        raise ValueError(f"Error generating embeddings with {provider}: {e}") from e


def store_embeddings_in_pgvector(
    embeddings_data: List[Tuple[str, List[float]]], db_url: str, collection_name: str
) -> int:
    """
    Store embeddings in PostgreSQL using PGVector.

    Args:
        embeddings_data: List of tuples (chunk_text, embedding_vector)
        db_url: PostgreSQL connection URL
        collection_name: Name of the vector collection

    Returns:
        Number of embeddings successfully stored

    Raises:
        ValueError: If storage fails or inputs are invalid
    """
    if not embeddings_data:
        raise ValueError("Embeddings data cannot be empty")

    if not db_url:
        raise ValueError("Database URL cannot be empty")

    if not collection_name:
        raise ValueError("Collection name cannot be empty")

    try:
        config = load_config()
        provider = get_active_provider()

        # Create embedding function for PGVector based on provider
        if provider == "openai":
            embedding_function = OpenAIEmbeddings(
                model=config["OPENAI_EMBEDDING_MODEL"],
                api_key=config["OPENAI_API_KEY"],
            )
        else:  # provider == "google"
            embedding_function = GoogleGenerativeAIEmbeddings(
                model=config["GOOGLE_EMBEDDING_MODEL"],
                google_api_key=config["GOOGLE_API_KEY"],
            )

        # Create PGVector store from pre-computed embeddings
        # The from_embeddings method stores already-computed embeddings
        # It expects a list of tuples of (text, embedding_vector)
        vectorstore = PGVector.from_embeddings(
            text_embeddings=embeddings_data,
            embedding=embedding_function,
            collection_name=collection_name,
            connection_string=db_url,
            use_jsonb=False,
        )

        return len(embeddings_data)

    except Exception as e:
        raise ValueError(f"Error storing embeddings in pgvector: {e}") from e
