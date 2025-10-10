import ollama
import requests
import json
import os
from typing import Optional
from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import TokenCounter, PromptValidator


class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, **kwargs) -> str:
        # Validate and truncate prompt if necessary
        validated_prompt = PromptValidator.validate_and_truncate(
            prompt, self.model_name
        )

        # Log token usage for debugging
        token_count = TokenCounter.count_tokens(validated_prompt, self.model_name)
        context_window = TokenCounter.get_context_window(self.model_name)
        print(
            f"Debug: Using {token_count}/{context_window} tokens for {self.model_name}"
        )

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=validated_prompt,
                options={
                    "temperature": kwargs.get("temperature", 0.1),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_predict": kwargs.get("max_tokens", 2048),
                },
            )
            # Check if Ollama returned an error response
            if "error" in response:
                return f"Model error: {response['error']}"
            return response["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"


class OpenAICompatibleProvider(LLMProvider):
    """Provider for OpenAI compatible APIs."""

    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.system_prompt = system_prompt

    def generate(self, prompt: str, **kwargs) -> str:
        # Validate and truncate prompt if necessary
        validated_prompt = PromptValidator.validate_and_truncate(
            prompt, self.model_name
        )

        # Log token usage for debugging
        token_count = TokenCounter.count_tokens(validated_prompt, self.model_name)
        context_window = TokenCounter.get_context_window(self.model_name)
        print(
            f"Debug: Using {token_count}/{context_window} tokens for {self.model_name}"
        )

        try:
            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Build messages array with system prompt support
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": validated_prompt})

            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 0.9),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120,  # Increased timeout for thinking models
            )
            response.raise_for_status()

            result = response.json()
            print(f"DEBUG PROVIDER: Got response from API")
            print(f"DEBUG PROVIDER: Response keys: {result.keys()}")

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"DEBUG PROVIDER: Content length: {len(content) if content else 0}")
                print(f"DEBUG PROVIDER: Content preview: {content[:100] if content else 'EMPTY'}")
                return content
            else:
                error_msg = f"Error: Unexpected response format: {result}"
                print(f"DEBUG PROVIDER: {error_msg}")
                return error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to API: {str(e)}"
            print(f"DEBUG PROVIDER: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(f"DEBUG PROVIDER: {error_msg}")
            return error_msg


class LMStudioProvider(OpenAICompatibleProvider):
    """Provider for LM Studio (local OpenAI-compatible server)."""

    def __init__(self, model_name: str, base_url: str = "http://localhost:1234"):
        # LM Studio typically doesn't require API keys for local access
        super().__init__(model_name, base_url, api_key=None)


class SarvamAIProvider(LLMProvider):
    """Provider for Sarvam AI M model."""

    def __init__(
        self,
        model_name: str = "sarvam-m",
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.base_url = "https://api.sarvam.ai"
        self.system_prompt = system_prompt

    def generate(self, prompt: str, **kwargs) -> str:
        # Validate and truncate prompt if necessary
        validated_prompt = PromptValidator.validate_and_truncate(
            prompt, self.model_name
        )

        # Log token usage for debugging
        token_count = TokenCounter.count_tokens(validated_prompt, self.model_name)
        context_window = TokenCounter.get_context_window(self.model_name)
        print(
            f"Debug: Using {token_count}/{context_window} tokens for {self.model_name}"
        )

        try:
            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["api-key"] = self.api_key

            # Build messages array with system prompt support
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": validated_prompt})

            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 0.9),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120,  # Increased timeout for thinking models
            )
            response.raise_for_status()

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: Unexpected response format: {result}"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to Sarvam AI API: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"


def get_provider(
    provider_type: str,
    model_name: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs,
) -> LLMProvider:
    """
    Factory function to create the appropriate provider based on type.

    Args:
        provider_type: Type of provider (ollama, lmstudio, openai, anthropic, sarvam)
        model_name: Model name to use
        base_url: API endpoint URL (for providers that need it)
        api_key: API key (for cloud providers)
        **kwargs: Additional provider-specific arguments

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider_type is unknown
    """
    provider_type = provider_type.lower()

    if provider_type == "ollama":
        return OllamaProvider(model_name)

    elif provider_type == "lmstudio":
        return LMStudioProvider(
            model_name=model_name, base_url=base_url or "http://localhost:1234"
        )

    elif provider_type == "openai":
        return OpenAICompatibleProvider(
            model_name=model_name,
            base_url=base_url or "https://api.openai.com/v1",
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            **kwargs,
        )

    elif provider_type == "anthropic":
        return OpenAICompatibleProvider(
            model_name=model_name,
            base_url=base_url or "https://api.anthropic.com/v1",
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            **kwargs,
        )

    elif provider_type == "sarvam":
        return SarvamAIProvider(
            model_name=model_name or "sarvam-m", api_key=api_key, **kwargs
        )

    elif provider_type == "openai-compatible":
        if not base_url:
            raise ValueError("base_url required for openai-compatible provider")
        return OpenAICompatibleProvider(
            model_name=model_name, base_url=base_url, api_key=api_key, **kwargs
        )

    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Supported: ollama, lmstudio, openai, anthropic, sarvam, openai-compatible"
        )
