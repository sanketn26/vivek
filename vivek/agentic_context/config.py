"""
Configuration Management
"""
from typing import Dict, Any
import yaml
import json
from pathlib import Path


class Config:
    """Configuration manager with presets and validation"""
    
    # Preset configurations
    PRESETS = {
        "development": {
            "retrieval": {
                "strategy": "tags_only",
                "max_results": 5,
                "min_score_threshold": 0.2
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": False,
                "max_candidates": 20
            },
            "semantic": {
                "enabled": False
            }
        },
        
        "production": {
            "retrieval": {
                "strategy": "hybrid",
                "max_results": 5,
                "min_score_threshold": 0.3
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": False,
                "max_candidates": 20
            },
            "semantic": {
                "enabled": True,
                "model": "microsoft/codebert-base",
                "cache_embeddings": True,
                "cache_size": 1000,
                "device": "cpu",
                "score_weight": 0.6,
                "min_score": 0.0
            }
        },
        
        "fast": {
            "retrieval": {
                "strategy": "tags_only",
                "max_results": 3,
                "min_score_threshold": 0.3
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": False,
                "max_candidates": 10
            },
            "semantic": {
                "enabled": False
            }
        },
        
        "accurate": {
            "retrieval": {
                "strategy": "hybrid",
                "max_results": 7,
                "min_score_threshold": 0.2
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": True,
                "max_candidates": 30
            },
            "semantic": {
                "enabled": True,
                "model": "sentence-transformers/all-mpnet-base-v2",
                "cache_embeddings": True,
                "cache_size": 2000,
                "device": "cpu",
                "score_weight": 0.7,
                "min_score": 0.0
            }
        },
        
        "lightweight": {
            "retrieval": {
                "strategy": "hybrid",
                "max_results": 5,
                "min_score_threshold": 0.3
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": False,
                "max_candidates": 15
            },
            "semantic": {
                "enabled": True,
                "model": "all-MiniLM-L6-v2",
                "cache_embeddings": True,
                "cache_size": 500,
                "device": "cpu",
                "score_weight": 0.5,
                "min_score": 0.0
            }
        },
        
        "auto": {
            "retrieval": {
                "strategy": "auto",
                "max_results": 5,
                "min_score_threshold": 0.3
            },
            "tag_normalization": {
                "enabled": True,
                "include_related_tags": False,
                "max_candidates": 20
            },
            "semantic": {
                "enabled": True,
                "model": "microsoft/codebert-base",
                "cache_embeddings": True,
                "cache_size": 1000,
                "device": "cpu",
                "score_weight": 0.6,
                "min_score": 0.0
            },
            "auto": {
                "simple_task_threshold": 2,
                "use_semantic_for_complex": True
            }
        }
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Dict[str, Any]:
        """Get a preset configuration"""
        if preset_name not in cls.PRESETS:
            raise ValueError(
                f"Unknown preset: {preset_name}. "
                f"Available: {list(cls.PRESETS.keys())}"
            )
        return cls.PRESETS[preset_name].copy()
    
    @classmethod
    def from_preset(cls, preset_name: str, **overrides) -> Dict[str, Any]:
        """
        Create config from preset with optional overrides
        
        Args:
            preset_name: Name of preset
            **overrides: Values to override in preset
            
        Returns:
            Configuration dict
        """
        config = cls.get_preset(preset_name)
        
        # Apply overrides
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys like "retrieval.strategy"
                parts = key.split(".")
                current = config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config[key] = value
        
        return config
    
    @classmethod
    def from_yaml(cls, filepath: str) -> Dict[str, Any]:
        """Load config from YAML file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def from_json(cls, filepath: str) -> Dict[str, Any]:
        """Load config from JSON file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(path, 'r') as f:
            return json.load(f)
    
    @classmethod
    def to_yaml(cls, config: Dict[str, Any], filepath: str):
        """Save config to YAML file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def to_json(cls, config: Dict[str, Any], filepath: str):
        """Save config to JSON file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If config is invalid
        """
        # Check required top-level keys
        required_keys = ["retrieval"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate retrieval strategy
        valid_strategies = ["tags_only", "embeddings_only", "hybrid", "auto"]
        strategy = config.get("retrieval", {}).get("strategy", "hybrid")
        if strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy: {strategy}. "
                f"Must be one of: {valid_strategies}"
            )
        
        # Validate semantic config if strategy uses embeddings
        if strategy in ["embeddings_only", "hybrid", "auto"]:
            if "semantic" not in config:
                raise ValueError(
                    f"Strategy '{strategy}' requires 'semantic' configuration"
                )
            
            semantic = config["semantic"]
            if not semantic.get("enabled", False):
                print(f"⚠️  Warning: Strategy '{strategy}' but semantic.enabled=False")
        
        return True
    
    @classmethod
    def print_config(cls, config: Dict[str, Any]):
        """Pretty print configuration"""
        print("=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        
        def print_dict(d, indent=0):
            for key, value in d.items():
                if isinstance(value, dict):
                    print("  " * indent + f"{key}:")
                    print_dict(value, indent + 1)
                else:
                    print("  " * indent + f"{key}: {value}")
        
        print_dict(config)
        print("=" * 60)


# Example usage function
def get_config(preset: str = "production", **overrides) -> Dict[str, Any]:
    """
    Convenience function to get configuration
    
    Args:
        preset: Preset name (development, production, fast, accurate, lightweight, auto)
        **overrides: Optional overrides
        
    Returns:
        Configuration dict
    """
    config = Config.from_preset(preset, **overrides)
    Config.validate(config)
    return config