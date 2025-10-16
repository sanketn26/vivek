"""
Centralized path setup utility to avoid duplication.
DRY principle: One place to manage Python path configuration.
"""

import sys
from pathlib import Path


def setup_src_path() -> None:
    """
    Add src directory to Python path for imports.

    This ensures vivek modules can be imported regardless of
    how the code is executed (as module, script, or in tests).
    """
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root (parent of src/)
    """
    return Path(__file__).parent.parent.parent.parent
