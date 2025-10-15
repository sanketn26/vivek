"""
Vivek AI Assistant - Simplified Architecture

A clean, maintainable AI coding assistant built with Domain-Driven Design principles.
"""

__version__ = "2.0.0"
__author__ = "Vivek AI Assistant"

from .application.orchestrators.simple_orchestrator import SimpleOrchestrator
from .application.services.vivek_application_service import VivekApplicationService

__all__ = ["SimpleOrchestrator", "VivekApplicationService"]
