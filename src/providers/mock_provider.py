"""
Mock provider implementation.

Implements the AiProvider interface with mock responses for testing purposes.
"""

import random
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage

from .base import AiProvider


class MockProvider(AiProvider):
    """Mock implementation of AiProvider for testing."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Mock provider.

        Args:
            config: Configuration dictionary (minimal requirements for mock)
        """
        super().__init__(config)
        # Set random seed for consistent mock behavior
        random.seed(42)

    def _validate_config(self) -> None:
        """Validate mock configuration (minimal requirements)."""
        # Mock provider has minimal configuration requirements
        pass

    def embed_query(self, text: str) -> List[float]:
        """Generate mock embeddings for a single query text."""
        # Create deterministic mock embedding based on text content
        random.seed(hash(text) % 2**32)  # Use text hash as seed for consistency
        return [random.uniform(-1, 1) for _ in range(768)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple documents."""
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings

    def invoke_llm(self, messages: List[BaseMessage]) -> str:
        """Generate a mock response from the LLM."""
        # Create a simple mock response based on the last message
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
                # Simple mock: echo back parts of the question
                if "?" in content:
                    return f"Mock response to: {content[:50]}{'...' if len(content) > 50 else ''}"
                else:
                    return f"Mock acknowledgment of: {content[:50]}{'...' if len(content) > 50 else ''}"

        return "Mock response: I am a mock AI provider for testing purposes."

    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions in mock embeddings."""
        return 768  # Same as Google to allow testing compatibility

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "mock"

    @classmethod
    def is_available(cls, config: Dict[str, Any]) -> bool:
        """Check if Mock provider is available (always True)."""
        return True

    def get_embedding_model_name(self) -> str:
        """Get the embedding model name."""
        return "mock-embedding-model"

    def get_llm_model_name(self) -> str:
        """Get the LLM model name."""
        return "mock-llm-model"