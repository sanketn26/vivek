import ollama
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
