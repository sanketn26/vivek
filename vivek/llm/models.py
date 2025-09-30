from abc import ABC, abstractmethod
from typing import Optional
import ollama

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

