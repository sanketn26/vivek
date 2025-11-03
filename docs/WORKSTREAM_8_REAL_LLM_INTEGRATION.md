# Workstream 8: Real LLM Integration & Testing

**Timeline**: Week 18-19 (2 weeks)
**Goal**: Integration with real LLMs and comprehensive quality metrics

**Prerequisites**: Workstreams 1-7 complete

---

## Overview

This workstream validates Vivek with real LLM providers (Ollama, OpenAI, Anthropic) and implements comprehensive testing with quality metrics collection.

### Current Limitations
- Only mock LLMs for testing
- No real LLM validation
- No performance benchmarking
- No quality metrics collection
- No model comparison

### What This Enables
- Production-ready LLM integration
- Performance benchmarks per model
- Quality metric collection and analysis
- Model comparison and selection
- Real-world validation

### Deliverables
- ✅ Ollama integration (local models)
- ✅ OpenAI integration (gpt-4, gpt-3.5)
- ✅ Anthropic integration (Claude)
- ✅ LLM provider factory
- ✅ Quality metrics framework
- ✅ Benchmark test suite
- ✅ Performance profiling
- ✅ Model comparison reports
- ✅ 40+ integration tests with real LLMs

---

## Part 1: LLM Provider Implementations

### File: `src/vivek/infrastructure/llm/ollama_provider.py` (Enhanced)

```python
"""Enhanced Ollama provider with metrics collection."""

import httpx
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from vivek.infrastructure.llm.base_provider import LLMProvider


@dataclass
class CallMetrics:
    """Metrics for a single LLM call."""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    temperature: float
    timestamp: float


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider with metrics."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b"
    ):
        self.base_url = base_url
        self.model = model
        self.metrics: List[CallMetrics] = []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text with metrics collection."""
        
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stream": False
                    }
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response
            text = data["message"]["content"]
            
            # Collect metrics
            response_time = time.time() - start_time
            metrics = CallMetrics(
                model=self.model,
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                response_time=response_time,
                temperature=temperature,
                timestamp=start_time
            )
            self.metrics.append(metrics)
            
            return text
        
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        if not self.metrics:
            return {}
        
        response_times = [m.response_time for m in self.metrics]
        total_tokens = sum(m.total_tokens for m in self.metrics)
        
        return {
            "calls": len(self.metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "total_tokens": total_tokens,
            "avg_tokens_per_call": total_tokens / len(self.metrics),
            "model": self.model
        }
    
    def clear_metrics(self):
        """Clear metrics history."""
        self.metrics = []
```

### File: `src/vivek/infrastructure/llm/openai_provider.py` (New)

```python
"""OpenAI API provider."""

import openai
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from vivek.infrastructure.llm.base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5)."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        organization: Optional[str] = None
    ):
        self.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            organization=organization
        )
        self.metrics: List[Dict] = []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API."""
        
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            text = response.choices[0].message.content
            
            # Collect metrics
            response_time = time.time() - start_time
            self.metrics.append({
                "model": self.model,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "response_time": response_time,
                "temperature": temperature,
                "cost": self._calculate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            })
            
            return text
        
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        if not self.metrics:
            return {}
        
        response_times = [m["response_time"] for m in self.metrics]
        total_tokens = sum(m["total_tokens"] for m in self.metrics)
        total_cost = sum(m.get("cost", 0) for m in self.metrics)
        
        return {
            "calls": len(self.metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "total_tokens": total_tokens,
            "total_cost": f"${total_cost:.4f}",
            "model": self.model
        }
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate API cost for GPT-4."""
        # GPT-4 pricing (as of 2024)
        prompt_cost = 0.03 / 1000 * prompt_tokens
        completion_cost = 0.06 / 1000 * completion_tokens
        return prompt_cost + completion_cost
```

### File: `src/vivek/infrastructure/llm/anthropic_provider.py` (New)

```python
"""Anthropic Claude API provider."""

import anthropic
import time
from typing import Dict, Any, Optional, List
from vivek.infrastructure.llm.base_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229"
    ):
        self.api_key = api_key
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.metrics: List[Dict] = []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using Claude."""
        
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            text = response.content[0].text
            
            # Collect metrics
            response_time = time.time() - start_time
            self.metrics.append({
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "response_time": response_time,
                "temperature": temperature
            })
            
            return text
        
        except Exception as e:
            print(f"Error calling Claude: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        if not self.metrics:
            return {}
        
        response_times = [m["response_time"] for m in self.metrics]
        total_tokens = sum(m.get("input_tokens", 0) + m.get("output_tokens", 0) 
                          for m in self.metrics)
        
        return {
            "calls": len(self.metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "total_tokens": total_tokens,
            "model": self.model
        }
```

---

## Part 2: Quality Metrics Framework

### File: `src/vivek/infrastructure/quality/quality_metrics.py`

```python
"""Quality metrics collection and analysis."""

from dataclasses import dataclass
from typing import Dict, Any, List
import json


@dataclass
class CodeQualityMetrics:
    """Metrics for generated code quality."""
    file_path: str
    
    # Correctness
    syntax_valid: bool
    imports_resolved: bool
    runs_without_error: bool
    
    # Style
    follows_style_guide: bool
    has_type_hints: float  # 0-1
    has_docstrings: float  # 0-1
    
    # Testing
    test_coverage: float  # 0-1
    tests_passing: bool
    
    # Performance
    execution_time_ms: float
    memory_usage_mb: float
    
    # Overall score
    overall_score: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "correctness": {
                "syntax": self.syntax_valid,
                "imports": self.imports_resolved,
                "runs": self.runs_without_error
            },
            "style": {
                "guide": self.follows_style_guide,
                "type_hints": self.has_type_hints,
                "docstrings": self.has_docstrings
            },
            "testing": {
                "coverage": self.test_coverage,
                "passing": self.tests_passing
            },
            "performance": {
                "execution_time_ms": self.execution_time_ms,
                "memory_usage_mb": self.memory_usage_mb
            },
            "overall": self.overall_score
        }


class QualityMetricsCollector:
    """Collect and aggregate quality metrics."""
    
    def __init__(self):
        self.metrics: List[CodeQualityMetrics] = []
    
    def add_metrics(self, metrics: CodeQualityMetrics):
        """Add metrics for a file."""
        self.metrics.append(metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        if not self.metrics:
            return {}
        
        scores = [m.overall_score for m in self.metrics]
        
        return {
            "files_analyzed": len(self.metrics),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "passing_files": sum(1 for m in self.metrics if m.overall_score >= 0.8),
            "coverage_average": sum(m.test_coverage for m in self.metrics) / len(self.metrics)
        }
    
    def export_report(self, filepath: str):
        """Export metrics to JSON report."""
        report = {
            "summary": self.get_summary(),
            "files": [m.to_dict() for m in self.metrics]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
```

---

## Part 3: Comprehensive Benchmark Suite

### File: `tests/integration/test_real_llm_benchmark.py`

```python
"""Benchmark tests with real LLMs."""

import pytest
import asyncio
from pathlib import Path
from vivek.infrastructure.llm.ollama_provider import OllamaProvider
from vivek.infrastructure.llm.openai_provider import OpenAIProvider
from vivek.infrastructure.quality.quality_metrics import QualityMetricsCollector


class TestRealLLMBenchmark:
    """Benchmark against real LLMs."""
    
    @pytest.fixture
    def ollama_provider(self):
        """Create Ollama provider."""
        try:
            return OllamaProvider(model="qwen2.5-coder:7b")
        except:
            pytest.skip("Ollama not available")
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector."""
        return QualityMetricsCollector()
    
    @pytest.mark.integration
    @pytest.mark.llm
    async def test_ollama_generate_simple_function(self, ollama_provider):
        """Test Ollama generates simple function correctly."""
        prompt = """Generate a Python function that adds two numbers.
        
Requirements:
- Include type hints
- Include docstring
- Handle edge cases
"""
        
        result = await ollama_provider.generate(
            prompt=prompt,
            system_prompt="You are an expert Python developer.",
            temperature=0.1
        )
        
        assert len(result) > 0
        assert "def " in result
        assert "->" in result  # Type hint
        assert "\"\"\"" in result  # Docstring
        
        # Check metrics
        metrics = ollama_provider.get_metrics()
        print(f"Ollama metrics: {metrics}")
        assert metrics["calls"] == 1
    
    @pytest.mark.integration
    @pytest.mark.llm
    async def test_ollama_generate_class(self, ollama_provider):
        """Test Ollama generates class correctly."""
        prompt = """Generate a Python class for a User with:
- id: int
- email: str
- created_at: datetime

Include validation methods."""
        
        result = await ollama_provider.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=1024
        )
        
        assert "class " in result
        assert "email" in result
        assert "__init__" in result or "def " in result
    
    @pytest.mark.integration
    @pytest.mark.benchmark
    async def test_response_time_benchmark(self, ollama_provider):
        """Benchmark response times."""
        prompts = [
            "Write a hello world function in Python.",
            "Create a list sorting function.",
            "Generate a Fibonacci implementation.",
        ]
        
        times = []
        for prompt in prompts:
            result = await ollama_provider.generate(prompt, temperature=0.1)
            metrics = ollama_provider.get_metrics()
            times.append(metrics["avg_response_time"])
        
        print(f"\nAverage response time: {sum(times)/len(times):.2f}s")
        assert all(t < 60 for t in times), "Response times too slow"
    
    @pytest.mark.integration
    @pytest.mark.llm
    async def test_token_efficiency(self, ollama_provider):
        """Test token efficiency."""
        prompt = "Generate a Python utility function."
        
        result = await ollama_provider.generate(prompt, temperature=0.1)
        metrics = ollama_provider.get_metrics()
        
        # Check token usage is reasonable
        avg_tokens = metrics["avg_tokens_per_call"]
        assert avg_tokens < 2000, "Using too many tokens"
```

---

## Part 4: Model Comparison Framework

### File: `src/vivek/infrastructure/quality/model_comparator.py`

```python
"""Compare models on quality metrics."""

from typing import List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class ModelComparison:
    """Comparison of models on a benchmark."""
    benchmark_name: str
    models: Dict[str, Dict[str, Any]]
    winner: str
    
    def to_report(self) -> str:
        """Generate human-readable report."""
        report = f"## {self.benchmark_name} Comparison\n\n"
        
        for model, metrics in self.models.items():
            report += f"### {model}\n"
            for key, value in metrics.items():
                report += f"- {key}: {value}\n"
            report += "\n"
        
        report += f"**Winner: {self.winner}**\n"
        
        return report


class ModelComparator:
    """Compare multiple models."""
    
    def __init__(self):
        self.comparisons: List[ModelComparison] = []
    
    def compare(
        self,
        benchmark_name: str,
        results: Dict[str, Dict[str, Any]]
    ) -> ModelComparison:
        """Compare models on a benchmark."""
        
        # Determine winner based on quality score
        winner = max(
            results.items(),
            key=lambda x: x[1].get("quality_score", 0)
        )[0]
        
        comparison = ModelComparison(
            benchmark_name=benchmark_name,
            models=results,
            winner=winner
        )
        
        self.comparisons.append(comparison)
        return comparison
    
    def generate_report(self, filepath: str):
        """Generate comparison report."""
        report = "# Model Comparison Report\n\n"
        
        for comp in self.comparisons:
            report += comp.to_report()
            report += "\n"
        
        with open(filepath, 'w') as f:
            f.write(report)
```

---

## Part 5: Deliverables Checklist

- [ ] Ollama provider enhanced with metrics
- [ ] OpenAI provider implemented
- [ ] Anthropic provider implemented
- [ ] LLM provider factory updated
- [ ] Quality metrics framework complete
- [ ] Benchmark suite passes with real LLMs
- [ ] Model comparison working
- [ ] Metrics reporting functional
- [ ] 40+ integration tests with real LLMs
- [ ] >85% code coverage

---

## Success Criteria

✅ All LLM providers working
✅ Metrics collected accurately
✅ Performance benchmarks < 60s per call
✅ Model comparisons show clear winner
✅ Quality metrics correlate with human review
✅ Cost tracking (for paid APIs) working
✅ 40+ integration tests pass
✅ >85% code coverage
