"""
Integration module for structured prompt architecture

This module provides a unified interface to integrate the structured workflow
architecture with the existing Vivek system, allowing for seamless adoption
and backward compatibility.
"""

import json
from typing import Dict, Any, Optional, Union

from vivek.llm.models import LLMProvider
from vivek.llm.planner import PlannerModel
from vivek.llm.structured_planner import StructuredPlannerModel
from vivek.llm.executor import BaseExecutor
from vivek.llm.structured_executor import StructuredExecutor
from vivek.core.structured_workflow import StructuredWorkflow
from vivek.core.prompt_templates import StructuredPromptBuilder
from vivek.core.context_condensation import ProgressiveContextManager
from vivek.core.enhanced_graph_nodes import (
    create_enhanced_planner_node,
    create_enhanced_executor_node,
    create_enhanced_reviewer_node,
    create_enhanced_format_response_node,
)
from vivek.core.performance_validator import PerformanceValidator, PerformanceOptimizer


class WorkflowIntegrationManager:
    """
    Manages integration between structured workflow and existing Vivek architecture

    This class provides:
    - Unified interface for structured and legacy workflows
    - Automatic performance optimization
    - Backward compatibility with existing code
    - Seamless migration path
    """

    def __init__(self, provider: LLMProvider, use_structured: bool = True):
        self.provider = provider
        self.use_structured = use_structured

        # Initialize components based on configuration
        if use_structured:
            self.structured_workflow = StructuredWorkflow()
            self.prompt_builder = StructuredPromptBuilder()
            self.context_manager = ProgressiveContextManager()
            self.performance_validator = PerformanceValidator()
            self.performance_optimizer = PerformanceOptimizer(
                self.performance_validator
            )

            # Create structured components
            self.structured_planner = StructuredPlannerModel(provider)
        else:
            self.structured_workflow = None
            self.prompt_builder = None
            self.context_manager = None
            self.performance_validator = None
            self.performance_optimizer = None
            self.structured_planner = None

        # Legacy components for compatibility
        self.legacy_planner = PlannerModel(provider)

    def get_planner(
        self, mode: str = "auto"
    ) -> Union[PlannerModel, StructuredPlannerModel]:
        """Get appropriate planner based on mode"""
        if mode == "structured" or (
            mode == "auto" and self.use_structured and self.structured_planner
        ):
            # Use structured planner if available, otherwise fall back to legacy
            if self.structured_planner:
                return self.structured_planner
        return self.legacy_planner

    def get_executor(self, mode: str, provider: LLMProvider) -> BaseExecutor:
        """Get appropriate executor based on mode"""
        if self.use_structured:
            # For now, return legacy executor since StructuredExecutor needs more work
            # TODO: Fix StructuredExecutor to inherit from BaseExecutor properly
            from vivek.llm.executor import get_executor as get_legacy_executor

            return get_legacy_executor(mode, provider)
        else:
            # Return legacy executor
            from vivek.llm.executor import get_executor as get_legacy_executor

            return get_legacy_executor(mode, provider)

    def optimize_for_model(self, model_name: str) -> Dict[str, Any]:
        """Optimize configuration for specific model"""
        if not self.use_structured:
            return {"optimization": "legacy_mode"}

        # Use performance optimizer to get recommendations
        if self.performance_optimizer and self.structured_workflow:
            optimized_workflow = self.performance_optimizer.optimize_workflow_for_model(
                model_name, self.structured_workflow
            )
            # Return configuration dict, not the workflow object itself
            return {
                "optimization": "applied",
                "model": model_name,
                "config": "optimized",
            }
        else:
            return {"optimization": "structured_components_not_initialized"}

    def run_performance_benchmarks(self) -> str:
        """Run performance benchmarks and return report"""
        if not self.use_structured:
            return "Performance validation only available in structured mode"

        benchmarks = []

        # Benchmark structured workflow
        if self.performance_validator and self.structured_workflow:
            workflow_benchmark = (
                self.performance_validator.validate_structured_workflow(
                    self.structured_workflow,
                    "Benchmark test input for structured workflow",
                )
            )
            benchmarks.append(workflow_benchmark)

        # Benchmark context condensation
        if self.performance_validator and self.context_manager:
            context_benchmark = (
                self.performance_validator.validate_context_condensation(
                    self.context_manager
                )
            )
            benchmarks.append(context_benchmark)

        # Generate report
        if self.performance_validator:
            return self.performance_validator.generate_performance_report()
        else:
            return "Performance validator not available in legacy mode"

    def get_workflow_insights(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights about workflow execution"""
        insights = {
            "workflow_type": "structured" if self.use_structured else "legacy",
            "performance_optimized": False,
            "context_management": "basic",
        }

        if self.use_structured:
            insights.update(
                {
                    "performance_optimized": True,
                    "context_management": "progressive",
                    "phases_available": [
                        "understand",
                        "decompose",
                        "detail",
                        "taskify",
                    ],
                    "perspectives_available": [
                        "user",
                        "critic",
                        "ops",
                        "debugger",
                        "future",
                        "sdet",
                    ],
                    "tdd_patterns": ["red", "green", "refactor"],
                }
            )

            # Add task plan insights if available
            if "structured_workflow" in task_plan:
                workflow_info = task_plan["structured_workflow"]
                insights["activities_count"] = workflow_info.get("activities_count", 0)
                insights["tasks_count"] = workflow_info.get("tasks_count", 0)

        return insights


class WorkflowCompatibilityLayer:
    """
    Compatibility layer for seamless integration with existing code

    This class ensures that existing Vivek code can use the structured
    workflow without modifications, while new code can take advantage
    of enhanced features.
    """

    def __init__(self, integration_manager: WorkflowIntegrationManager):
        self.integration_manager = integration_manager

    def analyze_request(self, user_input: str, context: str) -> Dict[str, Any]:
        """Analyze request with automatic workflow selection"""
        planner = self.integration_manager.get_planner()

        # Add context management if structured workflow is enabled
        if (
            self.integration_manager.use_structured
            and self.integration_manager.context_manager
        ):
            # Enhance context with structured workflow context
            enhanced_context = self._enhance_context_with_workflow(context)
            return planner.analyze_request(user_input, enhanced_context)
        else:
            return planner.analyze_request(user_input, context)

    def execute_enhanced_task(
        self, task_plan: Dict[str, Any], context: str, mode: str
    ) -> Dict[str, Any]:
        """Execute task with enhanced executor if available"""
        executor = self.integration_manager.get_executor(
            mode, self.integration_manager.provider
        )

        # Add workflow context if structured
        if (
            self.integration_manager.use_structured
            and self.integration_manager.context_manager
        ):
            enhanced_context = self._enhance_context_with_workflow(context)
            return executor.execute_task(task_plan, enhanced_context)
        else:
            return executor.execute_task(task_plan, context)

    def execute_task(
        self, task_plan: Dict[str, Any], context: str, mode: str
    ) -> Dict[str, Any]:
        """Execute task with enhanced executor if available"""
        executor = self.integration_manager.get_executor(
            mode, self.integration_manager.provider
        )

        # Add workflow context if structured
        if self.integration_manager.use_structured:
            enhanced_context = self._enhance_context_with_workflow(context)
            return executor.execute_task(task_plan, enhanced_context)
        else:
            return executor.execute_task(task_plan, context)

    def review_output(
        self, task_description: str, executor_output: str
    ) -> Dict[str, Any]:
        """Review output with enhanced reviewer if available"""
        planner = self.integration_manager.get_planner()

        return planner.review_output(task_description, executor_output)

    def _enhance_context_with_workflow(self, context: str) -> str:
        """Enhance context with structured workflow information"""
        if (
            not self.integration_manager.use_structured
            or not self.integration_manager.context_manager
        ):
            return context

        try:
            # Add workflow context summary
            context_summary = (
                self.integration_manager.context_manager.get_condensed_context(
                    "balanced"
                )
            )

            workflow_context = {
                "structured_workflow_enabled": True,
                "context_layers": len(self.integration_manager.context_manager.layers),
                "compression_strategy": context_summary.compression_strategy,
                "recent_memory_count": len(context_summary.short_term_memory),
                "medium_memory_count": len(context_summary.medium_term_memory),
            }

            # Merge with existing context
            if isinstance(context, str):
                try:
                    context_data = json.loads(context)
                except json.JSONDecodeError:
                    context_data = {"original_context": context}

                if isinstance(context_data, dict):
                    context_data["workflow_context"] = json.dumps(workflow_context)
                    return json.dumps(context_data, indent=2)
                else:
                    return context
            else:
                # Context is already a dict-like object, return as string
                return json.dumps(context, indent=2) if context else "{}"
        except Exception:
            # If anything fails, return original context
            return context


def create_enhanced_orchestrator(
    provider: LLMProvider,
    use_structured: bool = True,
    enable_performance_optimization: bool = True,
) -> WorkflowIntegrationManager:
    """
    Create an enhanced orchestrator with structured workflow integration

    Args:
        provider: LLM provider instance
        use_structured: Whether to enable structured workflow features
        enable_performance_optimization: Whether to enable automatic performance optimization

    Returns:
        Configured WorkflowIntegrationManager instance
    """
    integration_manager = WorkflowIntegrationManager(provider, use_structured)

    # Apply performance optimizations if enabled
    if enable_performance_optimization and use_structured:
        model_name = getattr(provider, "model_name", "qwen2.5-coder:7b")
        optimization_config = integration_manager.optimize_for_model(model_name)

        print(f"🚀 Applied performance optimizations for {model_name}")
        print(f"   Configuration: {optimization_config}")

    return integration_manager


# Utility functions for easy migration


def migrate_to_structured_workflow(
    existing_planner: PlannerModel,
) -> StructuredPlannerModel:
    """Migrate existing planner to structured workflow"""
    return StructuredPlannerModel(existing_planner.provider)


def enhance_existing_executor(existing_executor: BaseExecutor) -> StructuredExecutor:
    """Enhance existing executor with structured capabilities"""
    return StructuredExecutor(existing_executor.provider, existing_executor.mode)


def get_workflow_recommendations(
    user_request: str, project_context: str
) -> Dict[str, Any]:
    """
    Get workflow recommendations for a given request

    Returns recommendations on whether to use structured workflow
    and what optimizations to apply.
    """
    recommendations = {
        "recommended_workflow": "structured",
        "confidence": 0.8,
        "reasoning": "Structured workflow provides better task decomposition and quality",
        "optimizations": [
            "Enable context condensation for complex tasks",
            "Use multiple perspectives for architectural decisions",
            "Apply TDD patterns for implementation tasks",
        ],
    }

    # Analyze request complexity
    complexity_indicators = [
        "system",
        "architecture",
        "platform",
        "integration",
        "security",
        "performance",
        "scale",
        "complex",
    ]

    request_lower = user_request.lower()
    complexity_score = sum(
        1 for indicator in complexity_indicators if indicator in request_lower
    )

    if complexity_score > 2:
        recommendations["confidence"] = 0.9
        recommendations["reasoning"] = (
            "High complexity detected - structured workflow strongly recommended"
        )
        recommendations["optimizations"].append("Use comprehensive context management")
    elif complexity_score == 0:
        recommendations["confidence"] = 0.6
        recommendations["recommended_workflow"] = "legacy"
        recommendations["reasoning"] = (
            "Simple request - legacy workflow may be sufficient"
        )

    return recommendations
