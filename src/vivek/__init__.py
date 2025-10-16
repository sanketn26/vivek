"""
Vivek AI Assistant - Clean Architecture

A maintainable AI coding assistant built with SOLID principles and DDD.
Following: Single Responsibility, DRY, YAGNI, Dependency Injection.
"""

__version__ = "3.0.0"
__author__ = "Vivek AI Assistant"

# Main exports
from .application.orchestrators.simple_orchestrator import SimpleOrchestrator
from .application.services.vivek_application_service import VivekApplicationService
from .infrastructure.di_container import ServiceContainer

# Domain models
from .domain.workflow.models.task import Task, TaskStatus, TaskComplexity
from .domain.workflow.models.workflow import Workflow, WorkflowStatus
from .domain.planning.models.task_plan import TaskPlan, PlanStatus

__all__ = [
    # Application layer
    "SimpleOrchestrator",
    "VivekApplicationService",
    "ServiceContainer",
    # Domain models
    "Task",
    "TaskStatus",
    "TaskComplexity",
    "Workflow",
    "WorkflowStatus",
    "TaskPlan",
    "PlanStatus",
]
