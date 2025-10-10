"""Tests for prompt optimization and token counting.

This test suite validates:
1. Baseline token counts for all language × mode combinations
2. Prompt quality (no unused examples, proper structure)
3. Token counting functionality
4. Plugin performance (caching, etc.)
"""

import pytest
from unittest.mock import Mock, patch
from vivek.llm.provider import OllamaProvider
from vivek.llm.plugins.base.registry import get_registry, discover_plugins
from vivek.llm.executor import get_executor
from vivek.llm.constants import Mode


def count_tokens_simple(text: str) -> int:
    """Simple token counter (approximation).

    Real implementation would use tiktoken, but for testing purposes
    we use a simple word-based approximation: ~1.3 tokens per word.
    """
    words = len(text.split())
    return int(words * 1.3)


class TestPromptBaseline:
    """Baseline tests to capture current prompt token counts."""

    @pytest.fixture(autouse=True)
    def setup_plugins(self):
        """Ensure plugins are discovered before each test."""
        registry = get_registry()
        registry.clear_registry()
        discover_plugins()

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider for testing."""
        provider = Mock(spec=OllamaProvider)
        provider.generate.return_value = "Mock response"
        return provider

    @pytest.fixture
    def sample_task_plan(self):
        """Sample task plan for prompt generation."""
        return {
            "description": "Implement user authentication",
            "work_items": [
                {
                    "file_path": "src/auth.py",
                    "description": "Add login function",
                    "file_status": "new",
                    "mode": "coder",
                    "dependencies": [],
                }
            ],
        }

    def _get_prompt_and_count(self, language: str, mode: str, provider, task_plan):
        """Helper to get executor prompt and count tokens."""
        executor = get_executor(mode, provider, language)
        prompt = executor.build_prompt(task_plan, context="Test context")
        token_count = count_tokens_simple(prompt)
        return prompt, token_count

    def test_python_coder_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Python coder prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "python", Mode.CODER.value, mock_provider, sample_task_plan
        )

        # Record baseline (will be updated after optimization)
        # Current baseline: expect > 500 tokens (verbose)
        assert token_count > 100, f"Prompt too short: {token_count} tokens"
        print(f"\n[BASELINE] Python Coder: {token_count} tokens")

    def test_python_architect_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Python architect prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "python", Mode.ARCHITECT.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Python Architect: {token_count} tokens")

    def test_python_peer_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Python peer prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "python", Mode.PEER.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Python Peer: {token_count} tokens")

    def test_python_sdet_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Python SDET prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "python", Mode.SDET.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Python SDET: {token_count} tokens")

    def test_typescript_coder_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for TypeScript coder prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "typescript", Mode.CODER.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] TypeScript Coder: {token_count} tokens")

    def test_typescript_architect_prompt_baseline(
        self, mock_provider, sample_task_plan
    ):
        """Baseline test for TypeScript architect prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "typescript", Mode.ARCHITECT.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] TypeScript Architect: {token_count} tokens")

    def test_typescript_peer_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for TypeScript peer prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "typescript", Mode.PEER.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] TypeScript Peer: {token_count} tokens")

    def test_typescript_sdet_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for TypeScript SDET prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "typescript", Mode.SDET.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] TypeScript SDET: {token_count} tokens")

    def test_go_coder_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Go coder prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "go", Mode.CODER.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Go Coder: {token_count} tokens")

    def test_go_architect_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Go architect prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "go", Mode.ARCHITECT.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Go Architect: {token_count} tokens")

    def test_go_peer_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Go peer prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "go", Mode.PEER.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Go Peer: {token_count} tokens")

    def test_go_sdet_prompt_baseline(self, mock_provider, sample_task_plan):
        """Baseline test for Go SDET prompt."""
        prompt, token_count = self._get_prompt_and_count(
            "go", Mode.SDET.value, mock_provider, sample_task_plan
        )

        assert token_count > 100
        print(f"\n[BASELINE] Go SDET: {token_count} tokens")


class TestPromptQuality:
    """Tests for prompt quality and structure."""

    @pytest.fixture(autouse=True)
    def setup_plugins(self):
        """Ensure plugins are discovered before each test."""
        registry = get_registry()
        registry.clear_registry()
        discover_plugins()

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider for testing."""
        provider = Mock(spec=OllamaProvider)
        provider.generate.return_value = "Mock response"
        return provider

    @pytest.fixture
    def sample_task_plan(self):
        """Sample task plan for prompt generation."""
        return {
            "description": "Implement user authentication",
            "work_items": [
                {
                    "file_path": "src/auth.py",
                    "description": "Add login function",
                    "file_status": "new",
                    "mode": "coder",
                    "dependencies": [],
                }
            ],
        }

    def test_prompt_contains_required_sections(self, mock_provider, sample_task_plan):
        """Test that prompts contain all required sections."""
        executor = get_executor(Mode.CODER.value, mock_provider, "python")
        prompt = executor.build_prompt(sample_task_plan, context="Test context")

        # Check for required sections (flexible matching)
        prompt_upper = prompt.upper()
        assert "CONTEXT" in prompt_upper, "Prompt should contain CONTEXT section"
        assert "TASK" in prompt_upper, "Prompt should contain TASK section"
        assert (
            "WORK" in prompt_upper and "ITEMS" in prompt_upper
        ), "Prompt should contain WORK ITEMS section"
        assert "PROCESS" in prompt_upper, "Prompt should contain PROCESS section"
        assert (
            "OUTPUT" in prompt_upper and "FORMAT" in prompt_upper
        ), "Prompt should contain OUTPUT FORMAT section"

    def test_prompt_contains_language_conventions(
        self, mock_provider, sample_task_plan
    ):
        """Test that prompts include language-specific conventions."""
        # Python
        executor = get_executor(Mode.CODER.value, mock_provider, "python")
        prompt = executor.build_prompt(sample_task_plan, context="Test context")
        assert "Python" in prompt or "python" in prompt

        # TypeScript
        executor = get_executor(Mode.CODER.value, mock_provider, "typescript")
        prompt = executor.build_prompt(sample_task_plan, context="Test context")
        assert "TypeScript" in prompt or "typescript" in prompt

        # Go
        executor = get_executor(Mode.CODER.value, mock_provider, "go")
        prompt = executor.build_prompt(sample_task_plan, context="Test context")
        assert "Go" in prompt or "go" in prompt

    def test_no_code_examples_in_plugin_files(self):
        """Test that language plugin files don't contain massive code examples.

        This test will FAIL (RED) initially - we haven't deleted examples yet.
        After deleting example methods, it will pass (GREEN).
        """
        from vivek.llm.plugins.languages import python, typescript, go

        # Check that get_code_example helper methods don't exist
        for plugin_module in [python, typescript, go]:
            # Get the plugin class
            plugin_classes = [
                obj
                for name, obj in vars(plugin_module).items()
                if isinstance(obj, type) and name.endswith("LanguagePlugin")
            ]

            for plugin_class in plugin_classes:
                # Plugin class should not have example helper methods
                assert not hasattr(
                    plugin_class, "_get_python_coder_example"
                ), f"{plugin_class.__name__} still has _get_python_coder_example method"
                assert not hasattr(
                    plugin_class, "_get_typescript_coder_example"
                ), f"{plugin_class.__name__} still has _get_typescript_coder_example method"
                assert not hasattr(
                    plugin_class, "_get_go_coder_example"
                ), f"{plugin_class.__name__} still has _get_go_coder_example method"

    def test_instruction_token_limit(self, mock_provider, sample_task_plan):
        """Test that language-specific instructions are under 200 tokens.

        This test will FAIL (RED) initially - instructions are verbose.
        After compression, it will pass (GREEN).
        """
        registry = get_registry()

        # Test all language-mode combinations
        languages = ["python", "typescript", "go"]
        modes = ["coder", "architect", "peer", "sdet"]

        for language in languages:
            for mode in modes:
                plugin = registry.get_best_plugin(language, mode)
                if plugin:
                    instructions = plugin.get_language_specific_instructions(mode)
                    token_count = count_tokens_simple(instructions)

                    # Instructions should be concise (<200 tokens)
                    assert (
                        token_count < 200
                    ), f"{language}/{mode} instructions too long: {token_count} tokens"

    def test_minimal_convention_fields(self):
        """Test that LanguageConventions only has essential fields.

        This test will FAIL (RED) initially - conventions have many unused fields.
        After simplification, it will pass (GREEN).
        """
        from vivek.llm.plugins.base.language_plugin import LanguageConventions
        from dataclasses import fields

        # Get all fields in LanguageConventions
        convention_fields = {f.name for f in fields(LanguageConventions)}

        # Only these fields should exist (essential for plugin operation)
        essential_fields = {"language", "extensions"}

        # All other fields are unused bloat
        extra_fields = convention_fields - essential_fields

        assert len(extra_fields) == 0, (
            f"LanguageConventions has {len(extra_fields)} unused fields: {extra_fields}. "
            f"Only {essential_fields} are needed."
        )


class TestTokenCounting:
    """Tests for token counting functionality."""

    @pytest.fixture(autouse=True)
    def setup_plugins(self):
        """Ensure plugins are discovered before each test."""
        registry = get_registry()
        registry.clear_registry()
        discover_plugins()

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider for testing."""
        provider = Mock(spec=OllamaProvider)
        provider.generate.return_value = "Mock response"
        return provider

    @pytest.fixture
    def sample_task_plan(self):
        """Sample task plan for prompt generation."""
        return {
            "description": "Implement user authentication",
            "work_items": [
                {
                    "file_path": "src/auth.py",
                    "description": "Add login function",
                    "file_status": "new",
                    "mode": "coder",
                    "dependencies": [],
                }
            ],
        }

    def test_prompt_token_counting(self, mock_provider, sample_task_plan, caplog):
        """Test that executor logs token count.

        This test will FAIL (RED) initially - token counting not implemented.
        After implementation, it will pass (GREEN).
        """
        import logging

        caplog.set_level(logging.INFO)

        executor = get_executor(Mode.CODER.value, mock_provider, "python")
        prompt = executor.build_prompt(sample_task_plan, context="Test context")

        # Check that token count was logged
        assert any(
            "token" in record.message.lower() for record in caplog.records
        ), "Executor should log token count when building prompt"


class TestPluginPerformance:
    """Tests for plugin performance optimizations."""

    @pytest.fixture(autouse=True)
    def setup_plugins(self):
        """Ensure plugins are discovered before each test."""
        registry = get_registry()
        registry.clear_registry()
        discover_plugins()

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider for testing."""
        provider = Mock(spec=OllamaProvider)
        provider.generate.return_value = "Mock response"
        return provider

    def test_plugin_registry_caches_instances(self):
        """Test that plugin registry caches instances.

        This test will FAIL (RED) initially - no caching implemented.
        After implementation, it will pass (GREEN).
        """
        registry = get_registry()

        # Get plugin twice
        plugin1 = registry.get_best_plugin("python", "coder")
        plugin2 = registry.get_best_plugin("python", "coder")

        # Should return the same instance (cached)
        assert (
            plugin1 is plugin2
        ), "Registry should cache and return same plugin instance"
