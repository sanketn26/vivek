import ollama
from vivek.llm.models import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": kwargs.get("temperature", 0.1),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_predict": kwargs.get("max_tokens", 2048)
                }
            )
            # Check if Ollama returned an error response
            if "error" in response:
                return f"Model error: {response['error']}"
            return response["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"