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

    def __init__(self, model_name: str, base_url: str, api_key: Optional[str] = None, system_prompt: Optional[str] = None):
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
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
                'Content-Type': 'application/json',
            }
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            # Build messages array with system prompt support
            messages = []
            if self.system_prompt:
                messages.append({'role': 'system', 'content': self.system_prompt})
            messages.append({'role': 'user', 'content': validated_prompt})

            data = {
                'model': self.model_name,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.1),
                'top_p': kwargs.get('top_p', 0.9),
                'max_tokens': kwargs.get('max_tokens', 2048),
            }

            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected response format: {result}"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to API: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"


class LMStudioProvider(OpenAICompatibleProvider):
    """Provider for LM Studio (local OpenAI-compatible server)."""

    def __init__(self, model_name: str, base_url: str = "http://localhost:1234"):
        # LM Studio typically doesn't require API keys for local access
        super().__init__(model_name, base_url, api_key=None)


class SarvamAIProvider(LLMProvider):
    """Provider for Sarvam AI M model."""

    def __init__(self, model_name: str = "sarvam-m", api_key: Optional[str] = None, system_prompt: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv('SARVAM_API_KEY')
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
                'Content-Type': 'application/json',
            }
            if self.api_key:
                headers['api-key'] = self.api_key

            # Build messages array with system prompt support
            messages = []
            if self.system_prompt:
                messages.append({'role': 'system', 'content': self.system_prompt})
            messages.append({'role': 'user', 'content': validated_prompt})

            data = {
                'model': self.model_name,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.1),
                'top_p': kwargs.get('top_p', 0.9),
                'max_tokens': kwargs.get('max_tokens', 2048),
            }

            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected response format: {result}"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to Sarvam AI API: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
