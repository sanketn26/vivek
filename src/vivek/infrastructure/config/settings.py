"""Configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class LLMConfig(BaseSettings):
    """LLM provider configuration."""
    provider: str = "ollama"
    model: str = "qwen2.5-coder:7b"
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, gt=0)


class QualityConfig(BaseSettings):
    """Quality configuration."""
    threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    max_iterations: int = Field(default=1, ge=0, le=3)


class Settings(BaseSettings):
    """Application settings."""
    planner_llm: LLMConfig = LLMConfig()
    executor_llm: LLMConfig = LLMConfig()
    quality: QualityConfig = QualityConfig()

    model_config = SettingsConfigDict(env_file=".vivek/config.yml")