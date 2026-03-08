"""
AI Provider abstraction module.

This module provides a unified interface for different AI providers (OpenAI, Google, Mock)
allowing the business logic to work with any provider without specific implementations.
"""

from .factory import (
    get_ai_provider,
    select_provider_with_fallback,
    get_detailed_provider_info
)
from .base import AiProvider

__all__ = [
    "get_ai_provider",
    "select_provider_with_fallback",
    "get_detailed_provider_info",
    "AiProvider"
]