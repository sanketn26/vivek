"""Unit tests for Settings module default values."""

import pytest
from vivek.infrastructure.config.settings import Settings, LLMConfig, QualityConfig


class TestLLMConfigDefaults:
    """Test LLMConfig default values."""

    def test_llm_config_default_provider(self):
        """Test that default provider is 'ollama'."""
        config = LLMConfig()
        assert config.provider == "ollama"

    def test_llm_config_default_model(self):
        """Test that default model is 'qwen2.5-coder:7b'."""
        config = LLMConfig()
        assert config.model == "qwen2.5-coder:7b"

    def test_llm_config_default_temperature(self):
        """Test that default temperature is 0.1."""
        config = LLMConfig()
        assert config.temperature == 0.1

    def test_llm_config_default_max_tokens(self):
        """Test that default max_tokens is 4096."""
        config = LLMConfig()
        assert config.max_tokens == 4096

    def test_llm_config_temperature_is_float(self):
        """Test that temperature is a float."""
        config = LLMConfig()
        assert isinstance(config.temperature, float)

    def test_llm_config_max_tokens_is_int(self):
        """Test that max_tokens is an int."""
        config = LLMConfig()
        assert isinstance(config.max_tokens, int)

    def test_llm_config_provider_is_string(self):
        """Test that provider is a string."""
        config = LLMConfig()
        assert isinstance(config.provider, str)

    def test_llm_config_model_is_string(self):
        """Test that model is a string."""
        config = LLMConfig()
        assert isinstance(config.model, str)


class TestLLMConfigValidation:
    """Test LLMConfig validation constraints."""

    def test_llm_config_temperature_min_bound(self):
        """Test that temperature respects minimum bound (0.0)."""
        config = LLMConfig(temperature=0.0)
        assert config.temperature == 0.0

    def test_llm_config_temperature_max_bound(self):
        """Test that temperature respects maximum bound (1.0)."""
        config = LLMConfig(temperature=1.0)
        assert config.temperature == 1.0

    def test_llm_config_temperature_below_min_raises_error(self):
        """Test that temperature below minimum raises validation error."""
        with pytest.raises(ValueError):
            LLMConfig(temperature=-0.1)

    def test_llm_config_temperature_above_max_raises_error(self):
        """Test that temperature above maximum raises validation error."""
        with pytest.raises(ValueError):
            LLMConfig(temperature=1.1)

    def test_llm_config_max_tokens_must_be_positive(self):
        """Test that max_tokens must be greater than 0."""
        with pytest.raises(ValueError):
            LLMConfig(max_tokens=0)

    def test_llm_config_max_tokens_negative_raises_error(self):
        """Test that negative max_tokens raises validation error."""
        with pytest.raises(ValueError):
            LLMConfig(max_tokens=-1)

    def test_llm_config_large_temperature_values(self):
        """Test various valid temperature values."""
        valid_temps = [0.0, 0.1, 0.5, 0.9, 1.0]
        for temp in valid_temps:
            config = LLMConfig(temperature=temp)
            assert config.temperature == temp

    def test_llm_config_large_max_tokens_values(self):
        """Test various valid max_tokens values."""
        valid_tokens = [1, 100, 4096, 16000, 100000]
        for tokens in valid_tokens:
            config = LLMConfig(max_tokens=tokens)
            assert config.max_tokens == tokens


class TestLLMConfigCustomization:
    """Test LLMConfig with custom values."""

    def test_llm_config_custom_provider(self):
        """Test setting custom provider."""
        config = LLMConfig(provider="custom")
        assert config.provider == "custom"

    def test_llm_config_custom_model(self):
        """Test setting custom model."""
        config = LLMConfig(model="custom-model:13b")
        assert config.model == "custom-model:13b"

    def test_llm_config_custom_temperature(self):
        """Test setting custom temperature."""
        config = LLMConfig(temperature=0.7)
        assert config.temperature == 0.7

    def test_llm_config_custom_max_tokens(self):
        """Test setting custom max_tokens."""
        config = LLMConfig(max_tokens=8192)
        assert config.max_tokens == 8192

    def test_llm_config_all_custom_values(self):
        """Test setting all custom values."""
        config = LLMConfig(
            provider="custom",
            model="custom-model:7b",
            temperature=0.5,
            max_tokens=2048
        )

        assert config.provider == "custom"
        assert config.model == "custom-model:7b"
        assert config.temperature == 0.5
        assert config.max_tokens == 2048


class TestQualityConfigDefaults:
    """Test QualityConfig default values."""

    def test_quality_config_default_threshold(self):
        """Test that default threshold is 0.75."""
        config = QualityConfig()
        assert config.threshold == 0.75

    def test_quality_config_default_max_iterations(self):
        """Test that default max_iterations is 1."""
        config = QualityConfig()
        assert config.max_iterations == 1

    def test_quality_config_threshold_is_float(self):
        """Test that threshold is a float."""
        config = QualityConfig()
        assert isinstance(config.threshold, float)

    def test_quality_config_max_iterations_is_int(self):
        """Test that max_iterations is an int."""
        config = QualityConfig()
        assert isinstance(config.max_iterations, int)


class TestQualityConfigValidation:
    """Test QualityConfig validation constraints."""

    def test_quality_config_threshold_min_bound(self):
        """Test that threshold respects minimum bound (0.0)."""
        config = QualityConfig(threshold=0.0)
        assert config.threshold == 0.0

    def test_quality_config_threshold_max_bound(self):
        """Test that threshold respects maximum bound (1.0)."""
        config = QualityConfig(threshold=1.0)
        assert config.threshold == 1.0

    def test_quality_config_threshold_below_min_raises_error(self):
        """Test that threshold below minimum raises validation error."""
        with pytest.raises(ValueError):
            QualityConfig(threshold=-0.1)

    def test_quality_config_threshold_above_max_raises_error(self):
        """Test that threshold above maximum raises validation error."""
        with pytest.raises(ValueError):
            QualityConfig(threshold=1.1)

    def test_quality_config_max_iterations_min_bound(self):
        """Test that max_iterations can be 0."""
        config = QualityConfig(max_iterations=0)
        assert config.max_iterations == 0

    def test_quality_config_max_iterations_max_bound(self):
        """Test that max_iterations respects maximum bound (3)."""
        config = QualityConfig(max_iterations=3)
        assert config.max_iterations == 3

    def test_quality_config_max_iterations_above_max_raises_error(self):
        """Test that max_iterations above 3 raises validation error."""
        with pytest.raises(ValueError):
            QualityConfig(max_iterations=4)

    def test_quality_config_max_iterations_negative_raises_error(self):
        """Test that negative max_iterations raises validation error."""
        with pytest.raises(ValueError):
            QualityConfig(max_iterations=-1)

    def test_quality_config_valid_threshold_values(self):
        """Test various valid threshold values."""
        valid_thresholds = [0.0, 0.25, 0.5, 0.75, 1.0]
        for threshold in valid_thresholds:
            config = QualityConfig(threshold=threshold)
            assert config.threshold == threshold

    def test_quality_config_valid_max_iterations_values(self):
        """Test various valid max_iterations values."""
        valid_iterations = [0, 1, 2, 3]
        for iterations in valid_iterations:
            config = QualityConfig(max_iterations=iterations)
            assert config.max_iterations == iterations


class TestQualityConfigCustomization:
    """Test QualityConfig with custom values."""

    def test_quality_config_custom_threshold(self):
        """Test setting custom threshold."""
        config = QualityConfig(threshold=0.5)
        assert config.threshold == 0.5

    def test_quality_config_custom_max_iterations(self):
        """Test setting custom max_iterations."""
        config = QualityConfig(max_iterations=2)
        assert config.max_iterations == 2

    def test_quality_config_all_custom_values(self):
        """Test setting all custom values."""
        config = QualityConfig(threshold=0.9, max_iterations=3)
        assert config.threshold == 0.9
        assert config.max_iterations == 3


class TestSettingsDefaults:
    """Test Settings default values."""

    def test_settings_has_default_planner_llm(self):
        """Test that settings has a default planner LLM config."""
        settings = Settings()
        assert isinstance(settings.planner_llm, LLMConfig)
        assert settings.planner_llm.provider == "ollama"
        assert settings.planner_llm.model == "qwen2.5-coder:7b"

    def test_settings_has_default_executor_llm(self):
        """Test that settings has a default executor LLM config."""
        settings = Settings()
        assert isinstance(settings.executor_llm, LLMConfig)
        assert settings.executor_llm.provider == "ollama"
        assert settings.executor_llm.model == "qwen2.5-coder:7b"

    def test_settings_has_default_quality_config(self):
        """Test that settings has a default quality config."""
        settings = Settings()
        assert isinstance(settings.quality, QualityConfig)
        assert settings.quality.threshold == 0.75
        assert settings.quality.max_iterations == 1

    def test_settings_planner_llm_default_values(self):
        """Test that planner LLM has correct default values."""
        settings = Settings()
        assert settings.planner_llm.provider == "ollama"
        assert settings.planner_llm.model == "qwen2.5-coder:7b"
        assert settings.planner_llm.temperature == 0.1
        assert settings.planner_llm.max_tokens == 4096

    def test_settings_executor_llm_default_values(self):
        """Test that executor LLM has correct default values."""
        settings = Settings()
        assert settings.executor_llm.provider == "ollama"
        assert settings.executor_llm.model == "qwen2.5-coder:7b"
        assert settings.executor_llm.temperature == 0.1
        assert settings.executor_llm.max_tokens == 4096

    def test_settings_quality_default_values(self):
        """Test that quality config has correct default values."""
        settings = Settings()
        assert settings.quality.threshold == 0.75
        assert settings.quality.max_iterations == 1


class TestSettingsCustomization:
    """Test Settings with custom values."""

    def test_settings_custom_planner_llm(self):
        """Test setting custom planner LLM config."""
        planner_config = LLMConfig(provider="custom", model="custom-model:7b")
        settings = Settings(planner_llm=planner_config)
        assert settings.planner_llm.provider == "custom"
        assert settings.planner_llm.model == "custom-model:7b"

    def test_settings_custom_executor_llm(self):
        """Test setting custom executor LLM config."""
        executor_config = LLMConfig(temperature=0.5, max_tokens=2048)
        settings = Settings(executor_llm=executor_config)
        assert settings.executor_llm.temperature == 0.5
        assert settings.executor_llm.max_tokens == 2048

    def test_settings_custom_quality_config(self):
        """Test setting custom quality config."""
        quality_config = QualityConfig(threshold=0.9, max_iterations=3)
        settings = Settings(quality=quality_config)
        assert settings.quality.threshold == 0.9
        assert settings.quality.max_iterations == 3

    def test_settings_all_custom_values(self):
        """Test setting all custom values."""
        planner = LLMConfig(provider="custom1", model="model1:7b")
        executor = LLMConfig(provider="custom2", model="model2:7b")
        quality = QualityConfig(threshold=0.85, max_iterations=2)
        
        settings = Settings(
            planner_llm=planner,
            executor_llm=executor,
            quality=quality
        )

        assert settings.planner_llm.provider == "custom1"
        assert settings.executor_llm.provider == "custom2"
        assert settings.quality.threshold == 0.85
        assert settings.quality.max_iterations == 2


class TestSettingsIsolation:
    """Test that Settings instances are isolated."""

    def test_settings_instances_have_independent_configs(self):
        """Test that different Settings instances don't share configs."""
        settings1 = Settings(quality=QualityConfig(threshold=0.5))
        settings2 = Settings(quality=QualityConfig(threshold=0.9))

        assert settings1.quality.threshold == 0.5
        assert settings2.quality.threshold == 0.9

    def test_modifying_planner_llm_config_after_creation(self):
        """Test that modifying planner LLM config works correctly."""
        settings = Settings()
        original_provider = settings.planner_llm.provider
        
        settings.planner_llm = LLMConfig(provider="new_provider")
        assert settings.planner_llm.provider == "new_provider"
        assert original_provider != settings.planner_llm.provider

    def test_modifying_quality_config_after_creation(self):
        """Test that modifying quality config works correctly."""
        settings = Settings()
        original_threshold = settings.quality.threshold
        
        settings.quality = QualityConfig(threshold=0.5)
        assert settings.quality.threshold == 0.5
        assert original_threshold != settings.quality.threshold


class TestSettingsConsistency:
    """Test Settings consistency and initialization."""

    def test_settings_with_defaults_are_consistent(self):
        """Test that default settings are consistent across instances."""
        settings1 = Settings()
        settings2 = Settings()

        assert settings1.planner_llm.provider == settings2.planner_llm.provider
        assert settings1.executor_llm.temperature == settings2.executor_llm.temperature
        assert settings1.quality.threshold == settings2.quality.threshold

    def test_settings_planner_and_executor_llm_defaults_are_identical(self):
        """Test that planner and executor LLM defaults are the same."""
        settings = Settings()

        assert settings.planner_llm.provider == settings.executor_llm.provider
        assert settings.planner_llm.model == settings.executor_llm.model
        assert settings.planner_llm.temperature == settings.executor_llm.temperature
        assert settings.planner_llm.max_tokens == settings.executor_llm.max_tokens
