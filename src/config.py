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


def get_active_provider() -> Literal["openai", "google"]:
    """
    Get the currently active LLM provider.

    Returns:
        Either "openai" or "google"
    """
    return _active_provider


def switch_provider(provider_name: Literal["openai", "google"]) -> None:
    """
    Switch the active provider between "openai" and "google".

    The previous provider automatically becomes the fallback.

    Args:
        provider_name: Either "openai" or "google"

    Raises:
        ValueError: If provider_name is not "openai" or "google"
    """
    global _active_provider, _config

    if provider_name not in ("openai", "google"):
        raise ValueError(
            f'Invalid provider: "{provider_name}". '
            f'Must be either "openai" or "google".'
        )

    _active_provider = provider_name
    if _config:
        _config["ACTIVE_PROVIDER"] = _active_provider


def is_provider_available(provider: Literal["openai", "google", "mock"]) -> bool:
    """
    Check if a provider is available (has valid API key).

    Args:
        provider: Provider name ("openai", "google", or "mock")

    Returns:
        True if provider is available, False otherwise
    """
    if provider == "mock":
        return True

    config = _config or load_config()

    if provider == "openai":
        key = config.get("OPENAI_API_KEY", "").strip()
        return key and key != ""
    elif provider == "google":
        key = config.get("GOOGLE_API_KEY", "").strip()
        return key and key != ""

    return False


def select_provider_with_fallback(
    preferred_provider: Literal["openai", "google", "mock"]
) -> tuple[Literal["openai", "google", "mock"], bool]:
    """
    Select a provider with intelligent fallback logic.

    Args:
        preferred_provider: The preferred provider ("openai", "google", or "mock")

    Returns:
        Tuple of (selected_provider, fallback_used)

    Raises:
        ValueError: If no suitable provider is available (mock is never used as fallback)
    """
    # If mock is requested, use it directly
    if preferred_provider == "mock":
        return ("mock", False)

    # Check if preferred provider is available
    if is_provider_available(preferred_provider):
        return (preferred_provider, False)

    # Try fallback (but never to mock)
    fallback_provider = "google" if preferred_provider == "openai" else "openai"

    if is_provider_available(fallback_provider):
        return (fallback_provider, True)

    # No suitable provider available
    available_providers = []
    if is_provider_available("openai"):
        available_providers.append("openai")
    if is_provider_available("google"):
        available_providers.append("google")

    if available_providers:
        available_str = ", ".join(available_providers)
        error_msg = (
            f'Preferred provider "{preferred_provider}" is not available. '
            f'Available providers: {available_str}. '
            f'Please configure API keys or use --ai with an available provider.'
        )
    else:
        error_msg = (
            f'No AI providers are available. '
            f'Please configure OPENAI_API_KEY and/or GOOGLE_API_KEY in your .env file, '
            f'or use --ai mock for testing.'
        )

    raise ValueError(error_msg)


def get_provider_info(provider: Literal["openai", "google", "mock"]) -> dict:
    """
    Get information about a provider.

    Args:
        provider: Provider name

    Returns:
        Dictionary with provider information
    """
    config = _config or load_config()

    if provider == "mock":
        return {
            "name": "Mock",
            "model": "mock-embeddings",
            "dimensions": 768,  # Default mock dimensions
            "available": True,
            "base_url": "N/A",
            "description": "Mock provider for testing"
        }
    elif provider == "openai":
        base_url = config.get("OPENAI_BASE_URL")
        return {
            "name": "OpenAI",
            "model": config.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            "dimensions": 1536,  # OpenAI embedding dimensions
            "available": is_provider_available("openai"),
            "base_url": base_url if base_url else "https://api.openai.com/v1 (default)",
            "description": "OpenAI Embeddings API" + (" (Custom URL)" if base_url else "")
        }
    elif provider == "google":
        base_url = config.get("GOOGLE_BASE_URL")
        return {
            "name": "Google",
            "model": config.get("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
            "dimensions": 768,  # Google embedding dimensions
            "available": is_provider_available("google"),
            "base_url": base_url if base_url else "https://generativelanguage.googleapis.com (default)",
            "description": "Google Generative AI Embeddings" + (" (Custom URL)" if base_url else "")
        }

    return {}


# Load configuration on module import
try:
    load_config()
except ValueError as e:
    print(f"ERROR: Configuration failed to load:\n{e}", file=sys.stderr)
    sys.exit(1)
