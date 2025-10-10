"""Language detection utilities for Vivek."""

import os
from pathlib import Path
from typing import List, Dict, Optional
import yaml


class LanguageDetector:
    """Detect programming languages used in a project."""

    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "python": {
            "extensions": [".py", ".pyx", ".pyw"],
            "files": [
                "requirements.txt",
                "setup.py",
                "pyproject.toml",
                "Pipfile",
                "poetry.lock",
            ],
            "dirs": ["__pycache__", "venv", ".venv", "env", ".env"],
        },
        "typescript": {
            "extensions": [".ts", ".tsx", ".d.ts"],
            "files": ["tsconfig.json", "package.json", "yarn.lock", "pnpm-lock.yaml"],
            "dirs": ["node_modules", "dist", "build"],
        },
        "javascript": {
            "extensions": [".js", ".jsx", ".mjs", ".cjs"],
            "files": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
            "dirs": ["node_modules", "dist", "build"],
        },
        "go": {
            "extensions": [".go"],
            "files": ["go.mod", "go.sum", "Makefile"],
            "dirs": ["vendor"],
        },
        "rust": {
            "extensions": [".rs"],
            "files": ["Cargo.toml", "Cargo.lock"],
            "dirs": ["target", "cargo"],
        },
        "java": {
            "extensions": [".java"],
            "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "dirs": ["target", "build", ".gradle"],
        },
    }

    @classmethod
    def detect_project_languages(cls, project_root: str = ".") -> List[str]:
        """
        Detect programming languages used in the project.

        Args:
            project_root: Root directory of the project

        Returns:
            List of detected languages, ordered by file count
        """
        root_path = Path(project_root)
        if not root_path.exists():
            return ["python"]  # Default fallback

        language_counts = {}

        # Count files by extension
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                extension = file_path.suffix.lower()
                for lang, patterns in cls.LANGUAGE_PATTERNS.items():
                    if extension in patterns["extensions"]:
                        language_counts[lang] = language_counts.get(lang, 0) + 1

        # Check for language-specific files and directories
        for lang, patterns in cls.LANGUAGE_PATTERNS.items():
            # Check files
            for file_pattern in patterns["files"]:
                if (root_path / file_pattern).exists():
                    language_counts[lang] = (
                        language_counts.get(lang, 0) + 10
                    )  # Weight file presence higher

            # Check directories
            for dir_pattern in patterns["dirs"]:
                if (root_path / dir_pattern).exists():
                    language_counts[lang] = (
                        language_counts.get(lang, 0) + 5
                    )  # Weight dir presence

        # Sort by count (descending) and return language names
        sorted_languages = sorted(
            language_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [lang for lang, count in sorted_languages if count > 0]

    @classmethod
    def get_primary_language(cls, project_root: str = ".") -> str:
        """
        Get the primary programming language for the project.

        Args:
            project_root: Root directory of the project

        Returns:
            Primary language name, defaults to 'python'
        """
        languages = cls.detect_project_languages(project_root)
        return languages[0] if languages else "python"

    @classmethod
    def load_configured_languages(cls, project_root: str = ".") -> List[str]:
        """
        Load languages from Vivek configuration if available.

        Args:
            project_root: Root directory of the project

        Returns:
            List of configured languages, or auto-detected if no config
        """
        config_path = Path(project_root) / ".vivek" / "config.yml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    languages = config.get("project_settings", {}).get("language", [])
                    if languages:
                        return [lang.lower() for lang in languages]
            except Exception:
                pass

        # Fall back to auto-detection
        return cls.detect_project_languages(project_root)
