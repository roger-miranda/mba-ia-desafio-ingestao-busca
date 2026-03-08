"""
AI Provider Factory.

Factory pattern implementation for creating AI provider instances based on configuration.
Includes intelligent fallback logic and provider availability checking.
"""

from typing import Dict, Any, Tuple
from .base import AiProvider
from .openai_provider import OpenAiProvider
from .google_provider import GoogleProvider
from .mock_provider import MockProvider


# Registry of available providers
_PROVIDER_REGISTRY = {
    "openai": OpenAiProvider,
    "google": GoogleProvider,
    "mock": MockProvider,
}


def get_ai_provider(
    provider_name: str = None,
    config: Dict[str, Any] = None,
    use_fallback: bool = False,
    log_selection: bool = False
) -> AiProvider:
    """
    Create an AI provider instance with unified fallback and logging logic.

    This is the main provider factory function that handles:
    1. Provider resolution (from parameter or config)
    2. Intelligent fallback logic when requested
    3. Optional detailed logging
    4. Provider instance creation

    Args:
        provider_name: Name of provider ('openai', 'google', 'mock').
                      If None, uses config["AI_PROVIDER_PRIMARY"]
        config: Configuration dictionary with provider-specific settings
        use_fallback: If True, use fallback logic when primary provider unavailable
        log_selection: If True, log detailed provider selection information

    Returns:
        AiProvider instance

    Raises:
        ValueError: If provider_name is not supported or no suitable provider available
        ValueError: If config is None
    """
    if config is None:
        raise ValueError("Configuration is required")

    # Step 1: Determine preferred provider
    if provider_name is None:
        # Use primary provider from config
        preferred_provider = config["AI_PROVIDER_PRIMARY"]
        if log_selection:
            print(f"📋 Using primary provider from config: {preferred_provider}", flush=True)
    else:
        preferred_provider = provider_name
        if log_selection:
            print(f"🎯 Using specified provider: {preferred_provider}", flush=True)

    # Step 2: Apply fallback logic if requested
    fallback_used = False
    if use_fallback:
        resolved_provider, fallback_used = select_provider_with_fallback(preferred_provider, config)
        selected_provider = resolved_provider
    else:
        selected_provider = preferred_provider

    # Step 3: Log detailed information if requested
    if log_selection:
        provider_info = get_detailed_provider_info(selected_provider, config)

        if fallback_used:
            print(
                f"⚠️  Primary provider '{preferred_provider}' unavailable, "
                f"using fallback: {provider_info['name']}", flush=True
            )
        else:
            print(f"✅ Using AI provider: {provider_info['name']}", flush=True)

        # Log detailed information
        print(f"   Model: {provider_info['model']}", flush=True)
        print(f"   Base URL: {provider_info['base_url']}", flush=True)
        print(f"   Dimensions: {provider_info['dimensions']}", flush=True)
        print(f"   Status: {'Available' if provider_info['available'] else 'Mock mode'}", flush=True)

    # Step 4: Create and return provider instance
    selected_provider = selected_provider.lower()

    if selected_provider not in _PROVIDER_REGISTRY:
        available = ", ".join(_PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown provider: '{selected_provider}'. "
            f"Available providers: {available}"
        )

    provider_class = _PROVIDER_REGISTRY[selected_provider]
    try:
        return provider_class(config)
    except KeyError as e:
        raise ValueError(f"Missing configuration for {selected_provider} provider: {e}")
    except Exception as e:
        raise ValueError(f"Failed to initialize {selected_provider} provider: {e}")






def is_provider_available(provider_name: str, config: Dict[str, Any]) -> bool:
    """
    Check if a provider is available (has valid configuration).

    This function delegates availability checking to each provider implementation,
    removing hardcoded knowledge about provider-specific requirements from the factory.

    Args:
        provider_name: Provider name ("openai", "google", or "mock")
        config: Configuration dictionary

    Returns:
        True if provider is available, False otherwise
    """
    provider_name = provider_name.lower()

    # Check if provider is registered
    if provider_name not in _PROVIDER_REGISTRY:
        return False

    # Delegate to the provider's own availability check
    provider_class = _PROVIDER_REGISTRY[provider_name]
    return provider_class.is_available(config)


def select_provider_with_fallback(
    preferred_provider: str, config: Dict[str, Any]
) -> Tuple[str, bool]:
    """
    Select a provider with intelligent fallback logic.

    Args:
        preferred_provider: The preferred provider name
        config: Configuration dictionary

    Returns:
        Tuple of (selected_provider, fallback_used)

    Raises:
        ValueError: If no suitable provider is available
    """
    preferred_provider = preferred_provider.lower()

    # If mock is requested, use it directly
    if preferred_provider == "mock":
        return ("mock", False)

    # Check if preferred provider is available
    if is_provider_available(preferred_provider, config):
        return (preferred_provider, False)

    # Try fallback (but never to mock)
    fallback_provider = "google" if preferred_provider == "openai" else "openai"

    if is_provider_available(fallback_provider, config):
        return (fallback_provider, True)

    # No suitable provider available - list what's available
    available_providers = []
    for provider in ["openai", "google"]:
        if is_provider_available(provider, config):
            available_providers.append(provider)

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
            f'Please configure the required API keys in your .env file, '
            f'or use --ai mock for testing.'
        )

    raise ValueError(error_msg)


def get_detailed_provider_info(provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed information about a provider including configuration details.

    Args:
        provider_name: Provider name
        config: Configuration dictionary

    Returns:
        Dictionary with detailed provider information
    """
    provider_name = provider_name.lower()

    if provider_name == "mock":
        return {
            "name": "Mock",
            "model": "mock-embedding-model",
            "dimensions": 768,
            "available": True,
            "base_url": "N/A",
            "description": "Mock provider for testing"
        }
    elif provider_name == "openai":
        base_url = config.get("OPENAI_BASE_URL")
        return {
            "name": "OpenAI",
            "model": config.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            "dimensions": 1536,
            "available": is_provider_available("openai", config),
            "base_url": base_url if base_url else "https://api.openai.com/v1 (default)",
            "description": "OpenAI Embeddings API" + (" (Custom URL)" if base_url else "")
        }
    elif provider_name == "google":
        base_url = config.get("GOOGLE_BASE_URL")
        return {
            "name": "Google",
            "model": config.get("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
            "dimensions": 768,
            "available": is_provider_available("google", config),
            "base_url": base_url if base_url else "https://generativelanguage.googleapis.com (default)",
            "description": "Google Generative AI Embeddings" + (" (Custom URL)" if base_url else "")
        }

    raise ValueError(f"Unknown provider: {provider_name}")


