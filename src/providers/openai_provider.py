"""
OpenAI provider implementation.

Implements the AiProvider interface using OpenAI's API through LangChain.
"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from .base import AiProvider


class OpenAiProvider(AiProvider):
    """OpenAI implementation of AiProvider."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.

        Args:
            config: Configuration dictionary containing OpenAI settings
        """
        super().__init__(config)
        self._initialize_models()

    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        required_keys = ["OPENAI_API_KEY", "OPENAI_EMBEDDING_MODEL", "OPENAI_LLM_MODEL"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required OpenAI configuration: {key}")

    def _initialize_models(self) -> None:
        """Initialize OpenAI models."""
        # Initialize embeddings model
        openai_kwargs = {
            "model": self.config["OPENAI_EMBEDDING_MODEL"],
            "api_key": self.config["OPENAI_API_KEY"],
        }
        if self.config.get("OPENAI_BASE_URL"):
            openai_kwargs["base_url"] = self.config["OPENAI_BASE_URL"]

        self._embeddings = OpenAIEmbeddings(**openai_kwargs)

        # Initialize LLM model
        llm_kwargs = {
            "model": self.config.get("OPENAI_LLM_MODEL", "gpt-3.5-turbo"),
            "temperature": self.config.get("OPENAI_TEMPERATURE", 0.7),
            "max_tokens": self.config.get("OPENAI_MAX_TOKENS", 500),
            "api_key": self.config["OPENAI_API_KEY"],
        }
        if self.config.get("OPENAI_BASE_URL"):
            llm_kwargs["base_url"] = self.config["OPENAI_BASE_URL"]

        self._llm = ChatOpenAI(**llm_kwargs)

    def embed_query(self, text: str) -> List[float]:
        """Generate embeddings for a single query text."""
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self._embeddings.embed_documents(texts)

    def invoke_llm(self, messages: List[BaseMessage]) -> str:
        """Generate a response using OpenAI's LLM."""
        response = self._llm.invoke(messages)
        return response.content

    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions in OpenAI embeddings."""
        # text-embedding-3-small and text-embedding-ada-002 both use 1536 dimensions
        return 1536

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    @classmethod
    def is_available(cls, config: Dict[str, Any]) -> bool:
        """Check if OpenAI provider is available (has valid API key)."""
        api_key = config.get("OPENAI_API_KEY", "").strip()
        return bool(api_key)

    def get_embedding_model_name(self) -> str:
        """Get the embedding model name."""
        return self.config["OPENAI_EMBEDDING_MODEL"]

    def get_llm_model_name(self) -> str:
        """Get the LLM model name."""
        return self.config.get("OPENAI_LLM_MODEL", "gpt-3.5-turbo")