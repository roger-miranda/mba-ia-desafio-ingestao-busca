"""
Package initialization for RAG system.

This module loads and validates the configuration on import.
If configuration fails to load, the package import will fail with a clear error.

Expected DATABASE_URL format:
    postgresql://postgres:postgres@localhost:5432/rag
"""

import sys

# Import and initialize configuration
try:
    from src.config import load_config

    # Load config at package initialization time
    load_config()

except ValueError as e:
    print(f"ERROR: Failed to initialize RAG package: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected error during RAG package initialization: {e}", file=sys.stderr)
    sys.exit(1)

# Expose provider management functions for use by other modules
__all__ = []
