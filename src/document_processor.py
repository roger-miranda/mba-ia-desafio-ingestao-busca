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
import os
import certifi

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector


# Configure SSL certificates using certifi
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['REQUESTS_CA_BUNDLE'] = cert_path
os.environ['CURL_CA_BUNDLE'] = cert_path
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = cert_path

print(f"🔒 SSL certificates configured: {cert_path}", flush=True)


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
    documents: List[Document], ai_provider
) -> List[Tuple[str, List[float]]]:
    """
    Generate embeddings for a batch of documents using the specified provider.

    Args:
        documents: List of Document objects to embed
        ai_provider: AI provider instance to use for embedding generation

    Returns:
        List of tuples containing (chunk_text, embedding_vector)

    Raises:
        ValueError: If provider is invalid or if embedding generation fails
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")

    try:

        # Extract text content from documents
        texts = [doc.page_content for doc in documents]

        print(f"🤖 Using {ai_provider.get_provider_name()} provider with model {ai_provider.get_embedding_model_name()}")
        print(f"📏 Embedding dimensions: {ai_provider.get_embedding_dimensions()}")

        # Generate embeddings in batch
        embedding_vectors = ai_provider.embed_documents(texts)

        # Pair text with embeddings
        embeddings_data = list(zip(texts, embedding_vectors))

        if not embeddings_data:
            raise ValueError("No embeddings generated")

        print(f"✓ Generated {len(embeddings_data)} embeddings")
        return embeddings_data

    except Exception as e:
        raise ValueError(f"Error generating embeddings with {ai_provider.get_provider_name()}: {e}") from e


def store_embeddings_in_pgvector(
    embeddings_data: List[Tuple[str, List[float]]], db_url: str, collection_name: str, ai_provider
) -> int:
    """
    Store embeddings in PostgreSQL using PGVector.

    Args:
        embeddings_data: List of tuples (chunk_text, embedding_vector)
        db_url: PostgreSQL connection URL
        collection_name: Name of the vector collection
        ai_provider: AI provider instance to use for embedding operations

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

        # Create a LangChain embeddings wrapper for PGVector compatibility
        from langchain_core.embeddings import Embeddings

        class ProviderEmbeddingsWrapper(Embeddings):
            """Wrapper to make our AiProvider compatible with LangChain's PGVector."""

            def __init__(self, ai_provider):
                self.ai_provider = ai_provider

            def embed_documents(self, texts):
                return self.ai_provider.embed_documents(texts)

            def embed_query(self, text):
                return self.ai_provider.embed_query(text)

        embedding_function = ProviderEmbeddingsWrapper(ai_provider)

        # IMPORTANT: Clean existing data before inserting new embeddings
        # This prevents data accumulation across multiple ingestions
        print(f"🗑️  Cleaning existing data from collection '{collection_name}'...")
        import psycopg2

        try:
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()

            # Count existing embeddings before cleanup
            cur.execute("""
                SELECT COUNT(*)
                FROM langchain_pg_embedding
                WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = %s);
            """, (collection_name,))

            existing_count = cur.fetchone()[0]
            if existing_count > 0:
                print(f"   ⚠️  Found {existing_count} existing embeddings - removing them")

                # Delete existing embeddings for this collection
                cur.execute("""
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = %s);
                """, (collection_name,))

                conn.commit()
                print(f"   ✓ Removed {existing_count} old embeddings")
            else:
                print(f"   ✓ Collection is clean (no existing embeddings)")

            cur.close()
            conn.close()

        except Exception as cleanup_error:
            print(f"   ⚠️  Cleanup warning (continuing anyway): {cleanup_error}")

        # Create PGVector store from pre-computed embeddings
        # The from_embeddings method stores already-computed embeddings
        # It expects a list of tuples of (text, embedding_vector)
        # Note: This creates the vector store as a side effect (stores in database)
        PGVector.from_embeddings(
            text_embeddings=embeddings_data,
            embedding=embedding_function,
            collection_name=collection_name,
            connection=db_url,
        )

        return len(embeddings_data)

    except Exception as e:
        raise ValueError(f"Error storing embeddings in pgvector: {e}") from e
