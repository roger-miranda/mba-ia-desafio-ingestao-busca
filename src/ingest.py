"""
Main ingest orchestrator for the RAG system.

This module orchestrates the complete data ingestion pipeline:
1. Load PDF from document.pdf
2. Split into chunks (1000 chars, 150 overlap)
3. Generate embeddings using configured provider
4. Store embeddings in PostgreSQL with pgVector

Usage:
    python -m src.ingest
"""

import sys
import os
from typing import Literal

from src.config import load_config
from src.providers import get_ai_provider
from src.cli_parser import create_ai_provider_parser
from src.document_processor import (
    load_pdf_documents,
    chunk_documents,
    generate_embeddings_batch,
    store_embeddings_in_pgvector,
)


def ingest_pdf(ai_provider: Literal["openai", "google", "mock", None] = None) -> int:
    """
    Main ingestion orchestrator that chains all PDF processing steps.

    This function:
    1. Loads configuration
    2. Selects AI provider with intelligent fallback
    3. Validates PDF file exists
    4. Loads and chunks PDF
    5. Generates embeddings using selected provider
    6. Stores embeddings in PostgreSQL

    Args:
        ai_provider: AI provider to use ("openai", "google", "mock", or None for config default)

    Returns:
        Total count of embeddings successfully stored

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If any processing step fails or no provider is available
    """
    try:
        # Load and validate configuration
        print("🔧 Loading configuration...", flush=True)
        config = load_config()
        pdf_path = config["PDF_PATH"]
        database_url = config["DATABASE_URL"]
        collection_name = config["PG_VECTOR_COLLECTION_NAME"]

        # Resolve provider with complete fallback logic (logs internally)
        ai_provider_instance = get_ai_provider(ai_provider, config, use_fallback=True, log_selection=True)
        print("", flush=True)  # Empty line for readability

        # Validate PDF file exists
        print("📄 Validating PDF file...", flush=True)
        if not pdf_path:
            raise FileNotFoundError("PDF_PATH is not configured")

        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Step 1: Load PDF
        print(f"📖 Loading PDF from {pdf_path}...", flush=True)
        documents = load_pdf_documents(pdf_path)
        print(f"   ✓ Loaded {len(documents)} pages from PDF", flush=True)

        # Step 2: Chunk documents
        print("✂️  Chunking documents (1000 chars, 150 overlap)...", flush=True)
        chunks = chunk_documents(
            documents, chunk_size=1000, chunk_overlap=150
        )
        print(f"   ✓ Created {len(chunks)} chunks from PDF", flush=True)

        # Step 3: Generate embeddings
        print(
            f"🧠 Generating embeddings using {ai_provider_instance.get_provider_name()} provider...",
            flush=True,
        )
        embeddings_data = generate_embeddings_batch(chunks, ai_provider_instance)
        print(f"   ✓ Generated embeddings for {len(embeddings_data)} chunks", flush=True)

        # Step 4: Store in pgvector
        print("💾 Storing embeddings in PostgreSQL pgVector...", flush=True)
        count = store_embeddings_in_pgvector(
            embeddings_data, database_url, collection_name, ai_provider_instance
        )
        print(f"   ✓ Stored {count} embeddings in pgvector", flush=True)

        # Final summary
        print(f"\n🎉 SUCCESS: {count} embeddings successfully stored in pgvector")
        return count

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error during ingestion: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    examples = """
Examples:
  python -m src.ingest                    # Use primary provider from config
  python -m src.ingest --ai openai        # Force OpenAI provider
  python -m src.ingest --ai google        # Force Google provider
  python -m src.ingest --ai mock          # Use mock provider for testing
        """

    parser = create_ai_provider_parser(
        "Ingest PDF documents into vector database",
        examples
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    ingest_pdf(ai_provider=args.ai)
