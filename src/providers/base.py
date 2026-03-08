"""
Base classes for AI provider abstraction.

Defines the AiProvider interface that all implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage


class AiProvider(ABC):
    """
    Abstract base class for AI providers.

    Provides a unified interface for both embeddings and LLM functionality,
    allowing business logic to work with any provider implementation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration.

        Args:
            config: Dictionary containing provider-specific configuration
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate that all required configuration is present.

        Raises:
            ValueError: If required configuration is missing
        """
        pass

    @classmethod
    @abstractmethod
    def is_available(cls, config: Dict[str, Any]) -> bool:
        """
        Check if this provider is available (has valid configuration).

        This method allows checking provider availability without instantiating
        the provider, avoiding the overhead of full initialization.

        Args:
            config: Configuration dictionary

        Returns:
            True if provider is available and can be instantiated, False otherwise
        """
        pass

    # Embeddings methods
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a single query text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors, one for each input text
        """
        pass

    # LLM methods
    @abstractmethod
    def invoke_llm(self, messages: List[BaseMessage]) -> str:
        """
        Generate a response using the LLM.

        Args:
            messages: List of messages for the conversation

        Returns:
            The generated response text
        """
        pass

    # Provider metadata
    @abstractmethod
    def get_embedding_dimensions(self) -> int:
        """
        Get the number of dimensions in the embedding vectors.

        Returns:
            Number of dimensions in the embeddings
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name (e.g., 'openai', 'google', 'mock')
        """
        pass

    @abstractmethod
    def get_embedding_model_name(self) -> str:
        """
        Get the name of the embedding model being used.

        Returns:
            Embedding model name
        """
        pass

    @abstractmethod
    def get_llm_model_name(self) -> str:
        """
        Get the name of the LLM model being used.

        Returns:
            LLM model name
        """
        pass