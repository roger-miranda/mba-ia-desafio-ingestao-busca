import os
import sys
from typing import Dict, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required environment variables for the system to function
# At least one of GOOGLE_API_KEY or OPENAI_API_KEY must be provided
REQUIRED_VARS = [
    "DATABASE_URL",
    "PG_VECTOR_COLLECTION_NAME",
    "PDF_PATH",
    "GOOGLE_EMBEDDING_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "GOOGLE_LLM_MODEL",
    "OPENAI_LLM_MODEL",
    "AI_PROVIDER_PRIMARY",
]

# At least one of these provider API keys must be configured
PROVIDER_VARS = [
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
]

# Global configuration dictionary
_config: Dict = {}
_active_provider: Literal["openai", "google"] = "openai"


def load_config() -> Dict:
    """
    Load and validate environment configuration.

    Loads variables from .env file and validates that all required
    variables are present and non-empty.

    Returns:
        Dictionary containing all environment variables and current provider

    Raises:
        ValueError: If any required environment variables are missing or empty
    """
    global _config, _active_provider

    # Check for missing or empty required variables
    missing_vars = []
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if not value or value.strip() == "":
            missing_vars.append(var)

    if missing_vars:
        error_msg = (
            f"Missing required environment variables:\n"
            f"  {', '.join(missing_vars)}\n\n"
            f"Please set these variables in your .env file or environment."
        )
        raise ValueError(error_msg)

    # Check that at least one provider API key is configured
    provider_keys = [os.getenv(var, "").strip() for var in PROVIDER_VARS]
    if not any(provider_keys):
        error_msg = (
            f"At least one API key must be configured:\n"
            f"  - GOOGLE_API_KEY or OPENAI_API_KEY\n\n"
            f"Please set at least one in your .env file or environment."
        )
        raise ValueError(error_msg)

    # Build config dictionary
    _config = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "PG_VECTOR_COLLECTION_NAME": os.getenv("PG_VECTOR_COLLECTION_NAME"),
        "PDF_PATH": os.getenv("PDF_PATH"),
        "GOOGLE_EMBEDDING_MODEL": os.getenv("GOOGLE_EMBEDDING_MODEL"),
        "OPENAI_EMBEDDING_MODEL": os.getenv("OPENAI_EMBEDDING_MODEL"),
        "GOOGLE_LLM_MODEL": os.getenv("GOOGLE_LLM_MODEL"),
        "OPENAI_LLM_MODEL": os.getenv("OPENAI_LLM_MODEL"),
        "AI_PROVIDER_PRIMARY": os.getenv("AI_PROVIDER_PRIMARY"),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
        "GOOGLE_BASE_URL": os.getenv("GOOGLE_BASE_URL"),
        "ACTIVE_PROVIDER": _active_provider,
    }

    # Determine primary provider from config
    primary_provider = os.getenv("AI_PROVIDER_PRIMARY", "openai").strip().lower()
    if primary_provider not in ("openai", "google"):
        primary_provider = "openai"  # Default fallback

    _active_provider = primary_provider
    _config["ACTIVE_PROVIDER"] = _active_provider

    return _config












# Load configuration on module import
try:
    load_config()
except ValueError as e:
    print(f"ERROR: Configuration failed to load:\n{e}", file=sys.stderr)
    sys.exit(1)
