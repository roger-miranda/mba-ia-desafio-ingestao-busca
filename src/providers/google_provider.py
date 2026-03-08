"""
Google provider implementation.

Implements the AiProvider interface using Google's Generative AI through LangChain.
"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from .base import AiProvider


class GoogleProvider(AiProvider):
    """Google implementation of AiProvider."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google provider.

        Args:
            config: Configuration dictionary containing Google settings
        """
        super().__init__(config)
        self._initialize_models()

    def _validate_config(self) -> None:
        """Validate Google configuration."""
        required_keys = ["GOOGLE_API_KEY", "GOOGLE_EMBEDDING_MODEL"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required Google configuration: {key}")

    def _initialize_models(self) -> None:
        """Initialize Google models."""
        # Initialize embeddings model
        google_embeddings_kwargs = {
            "model": self.config["GOOGLE_EMBEDDING_MODEL"],
            "google_api_key": self.config["GOOGLE_API_KEY"],
        }

        self._embeddings = GoogleGenerativeAIEmbeddings(**google_embeddings_kwargs)

        # Initialize LLM model
        llm_kwargs = {
            "model": self.config.get("GOOGLE_LLM_MODEL", "gemini-pro"),
            "temperature": self.config.get("GOOGLE_TEMPERATURE", 0.7),
            "max_output_tokens": self.config.get("GOOGLE_MAX_TOKENS", 500),
            "google_api_key": self.config["GOOGLE_API_KEY"],
        }

        self._llm = ChatGoogleGenerativeAI(**llm_kwargs)

    def embed_query(self, text: str) -> List[float]:
        """Generate embeddings for a single query text."""
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self._embeddings.embed_documents(texts)

    def invoke_llm(self, messages: List[BaseMessage]) -> str:
        """Generate a response using Google's LLM."""
        response = self._llm.invoke(messages)
        return response.content

    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions in Google embeddings."""
        # models/embedding-001 uses 768 dimensions
        return 768

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "google"

    @classmethod
    def is_available(cls, config: Dict[str, Any]) -> bool:
        """Check if Google provider is available (has valid API key)."""
        api_key = config.get("GOOGLE_API_KEY", "").strip()
        return bool(api_key)

    def get_embedding_model_name(self) -> str:
        """Get the embedding model name."""
        return self.config["GOOGLE_EMBEDDING_MODEL"]

    def get_llm_model_name(self) -> str:
        """Get the LLM model name."""
        return self.config.get("GOOGLE_LLM_MODEL", "gemini-pro")