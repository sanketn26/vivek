"""
Unit tests for agentic_context.config module
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path

from vivek.agentic_context.config import Config, get_config


class TestConfig:
    """Test Config class functionality"""

    def test_get_preset_valid(self):
        """Test getting valid presets"""
        config = Config.get_preset("production")
        assert isinstance(config, dict)
        assert "retrieval" in config
        assert "semantic" in config
        assert config["retrieval"]["strategy"] == "hybrid"
        assert config["semantic"]["enabled"] is True

    def test_get_preset_invalid(self):
        """Test getting invalid preset raises error"""
        with pytest.raises(ValueError, match="Unknown preset"):
            Config.get_preset("nonexistent")

    def test_from_preset_basic(self):
        """Test creating config from preset"""
        config = Config.from_preset("development")
        assert config["retrieval"]["strategy"] == "tags_only"
        assert config["semantic"]["enabled"] is False

    def test_from_preset_with_overrides(self):
        """Test creating config from preset with overrides"""
        config = Config.from_preset("production", **{"retrieval.max_results": 10})
        assert config["retrieval"]["max_results"] == 10
        assert config["retrieval"]["strategy"] == "hybrid"  # unchanged

    def test_from_preset_with_nested_overrides(self):
        """Test creating config with nested key overrides"""
        config = Config.from_preset(
            "production",
            **{"retrieval.max_results": 8, "semantic.model": "test-model"}
        )
        assert config["retrieval"]["max_results"] == 8
        assert config["semantic"]["model"] == "test-model"

    @pytest.mark.parametrize("preset", ["development", "production", "fast", "accurate", "lightweight", "auto"])
    def test_all_presets_valid(self, preset):
        """Test that all presets are valid"""
        config = Config.from_preset(preset)
        assert Config.validate(config) is True

    def test_validate_valid_config(self):
        """Test validating a valid config"""
        config = Config.from_preset("production")
        assert Config.validate(config) is True

    def test_validate_missing_required_key(self):
        """Test validation fails for missing required keys"""
        config = {"incomplete": "config"}
        with pytest.raises(ValueError, match="Missing required key: retrieval"):
            Config.validate(config)

    def test_validate_invalid_strategy(self):
        """Test validation fails for invalid strategy"""
        config = {
            "retrieval": {"strategy": "invalid_strategy"}
        }
        with pytest.raises(ValueError, match="Invalid strategy"):
            Config.validate(config)

    def test_validate_missing_semantic_for_embeddings(self):
        """Test validation fails when semantic config missing for embeddings strategy"""
        config = {
            "retrieval": {"strategy": "hybrid"}
        }
        with pytest.raises(ValueError, match="requires 'semantic' configuration"):
            Config.validate(config)

    def test_to_yaml_and_from_yaml(self):
        """Test saving and loading config as YAML"""
        config = Config.from_preset("fast", max_results=3)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name

        try:
            Config.to_yaml(config, yaml_path)
            loaded_config = Config.from_yaml(yaml_path)

            assert loaded_config["retrieval"]["max_results"] == 3
            assert loaded_config["retrieval"]["strategy"] == "tags_only"
        finally:
            Path(yaml_path).unlink()

    def test_to_json_and_from_json(self):
        """Test saving and loading config as JSON"""
        config = Config.from_preset("accurate", max_results=7)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            Config.to_json(config, json_path)
            loaded_config = Config.from_json(json_path)

            assert loaded_config["retrieval"]["max_results"] == 7
            assert loaded_config["retrieval"]["strategy"] == "hybrid"
        finally:
            Path(json_path).unlink()

    def test_from_yaml_file_not_found(self):
        """Test loading from non-existent YAML file"""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("nonexistent.yaml")

    def test_from_json_file_not_found(self):
        """Test loading from non-existent JSON file"""
        with pytest.raises(FileNotFoundError):
            Config.from_json("nonexistent.json")

    def test_print_config(self, capsys):
        """Test pretty printing config"""
        config = Config.from_preset("lightweight")
        Config.print_config(config)

        captured = capsys.readouterr()
        assert "CONFIGURATION" in captured.out
        assert "retrieval:" in captured.out
        assert "semantic:" in captured.out


class TestGetConfigFunction:
    """Test the convenience get_config function"""

    def test_get_config_default(self):
        """Test get_config with default preset"""
        config = get_config()
        assert config["retrieval"]["strategy"] == "hybrid"
        assert config["semantic"]["enabled"] is True

    def test_get_config_with_preset(self):
        """Test get_config with specific preset"""
        config = get_config("fast")
        assert config["retrieval"]["strategy"] == "tags_only"
        assert config["semantic"]["enabled"] is False

    def test_get_config_with_overrides(self):
        """Test get_config with overrides"""
        config = get_config("production", **{"retrieval.max_results": 10})
        assert config["retrieval"]["max_results"] == 10
        assert config["retrieval"]["strategy"] == "hybrid"

    def test_get_config_validates(self):
        """Test that get_config validates the final config"""
        config = get_config("production")
        # Should not raise any exceptions
        assert isinstance(config, dict)

    def test_get_config_invalid_preset(self):
        """Test get_config with invalid preset"""
        with pytest.raises(ValueError):
            get_config("invalid_preset")