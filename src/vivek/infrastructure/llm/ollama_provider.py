"""
Concrete Ollama LLM provider implementation.
"""

from typing import Optional
from .llm_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """LLM provider using Ollama."""

    def __init__(
        self, model_name: str, base_url: str = "http://localhost:11434", timeout: int = 120
    ):
        """
        Initialize Ollama provider.

        Args:
            model_name: Name of the Ollama model (e.g., 'qwen2.5-coder:7b')
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        super().__init__(model_name)
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[object] = None

    def _get_client(self):
        """Lazy-load the ollama client."""
        if self._client is None:
            try:
                import ollama

                self._client = ollama.Client(host=self.base_url, timeout=self.timeout)
            except ImportError:
                raise RuntimeError(
                    "ollama package not installed. Install with: pip install ollama"
                )
        return self._client

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated text

        Raises:
            RuntimeError: If Ollama is not available or request fails
        """
        try:
            client = self._get_client()
            response = client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": temperature},
            )
            return response["response"]
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}") from e

    def is_available(self) -> bool:
        """
        Check if Ollama is available and model is loaded.

        Returns:
            True if available, False otherwise
        """
        try:
            client = self._get_client()
            # List models to check connection
            models = client.list()
            # Check if our model is available
            model_names = [model["name"] for model in models.get("models", [])]
            return self.model_name in model_names
        except Exception:
            return False
