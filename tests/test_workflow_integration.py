"""
Tests for workflow integration components.
"""

import pytest
from unittest.mock import Mock, patch

from vivek.core.workflow_integration import (
    WorkflowIntegrationManager,
    WorkflowCompatibilityLayer,
    get_workflow_recommendations,
)
from vivek.llm.models import LLMProvider


class TestWorkflowIntegrationManager:
    """Test cases for WorkflowIntegrationManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_provider = Mock(spec=LLMProvider)
        self.mock_provider.model_name = "qwen2.5-coder:7b"

    def test_initialization_structured_mode(self):
        """Test initialization in structured mode"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=True)

        assert manager.use_structured == True
        assert manager.structured_workflow is not None
        assert manager.structured_planner is not None
        assert manager.context_manager is not None
        assert manager.legacy_planner is not None

    def test_initialization_legacy_mode(self):
        """Test initialization in legacy mode"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=False)

        assert manager.use_structured == False
        assert manager.structured_workflow is None
        assert manager.structured_planner is None
        assert manager.context_manager is None
        assert manager.legacy_planner is not None

    def test_get_planner_structured_mode(self):
        """Test getting planner in structured mode"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=True)

        planner = manager.get_planner("auto")
        # Should return structured planner if available
        assert planner is not None

        legacy_planner = manager.get_planner("legacy")
        assert legacy_planner == manager.legacy_planner

    def test_optimize_for_model(self):
        """Test model optimization"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=True)

        # Test optimization for different model sizes
        small_model_config = manager.optimize_for_model("qwen2.5-coder:3b")
        medium_model_config = manager.optimize_for_model("qwen2.5-coder:7b")
        large_model_config = manager.optimize_for_model("qwen2.5-coder:14b")

        # All should return configuration dicts
        assert isinstance(small_model_config, dict)
        assert isinstance(medium_model_config, dict)
        assert isinstance(large_model_config, dict)

    def test_workflow_insights(self):
        """Test workflow insights generation"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=True)

        # Mock task plan with structured workflow info
        task_plan = {
            "description": "test task",
            "structured_workflow": {
                "activities_count": 3,
                "tasks_count": 5,
                "phases": ["understand", "decompose", "detail", "taskify"],
            },
        }

        insights = manager.get_workflow_insights(task_plan)

        assert insights["workflow_type"] == "structured"
        assert insights["performance_optimized"] == True
        assert insights["context_management"] == "progressive"
        assert "activities_count" in insights
        assert "tasks_count" in insights


class TestWorkflowCompatibilityLayer:
    """Test cases for WorkflowCompatibilityLayer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_provider = Mock(spec=LLMProvider)
        self.integration_manager = WorkflowIntegrationManager(
            self.mock_provider, use_structured=True
        )
        self.compatibility_layer = WorkflowCompatibilityLayer(self.integration_manager)

    def test_analyze_request_enhancement(self):
        """Test that analyze_request enhances context when structured"""
        # Mock structured planner
        self.integration_manager.structured_planner = Mock()
        self.integration_manager.structured_planner.analyze_request.return_value = {
            "type": "execution_complete",
            "payload": {"output": {"description": "test", "mode": "coder"}},
        }

        result = self.compatibility_layer.analyze_request(
            "test request", "test context"
        )

        assert "type" in result
        assert result["type"] == "execution_complete"

        # Should have called structured planner
        self.integration_manager.structured_planner.analyze_request.assert_called_once()

    def test_context_enhancement(self):
        """Test context enhancement with workflow information"""
        context = '{"existing": "data"}'
        enhanced_context = self.compatibility_layer._enhance_context_with_workflow(
            context
        )

        # Should return enhanced context or original if enhancement fails
        assert enhanced_context is not None

        # If enhancement worked, should be different from original
        # (This is a basic check - actual enhancement depends on implementation)
        assert isinstance(enhanced_context, str)


class TestWorkflowRecommendations:
    """Test cases for workflow recommendations"""

    def test_get_workflow_recommendations_complex_request(self):
        """Test recommendations for complex request"""
        recommendations = get_workflow_recommendations(
            "Design a microservices architecture for e-commerce platform with user authentication, payment processing, and inventory management",
            "Python project with multiple services",
        )

        assert recommendations["recommended_workflow"] == "structured"
        assert recommendations["confidence"] >= 0.8
        assert "reasoning" in recommendations
        assert "optimizations" in recommendations
        assert len(recommendations["optimizations"]) > 0

    def test_get_workflow_recommendations_simple_request(self):
        """Test recommendations for simple request"""
        recommendations = get_workflow_recommendations(
            "Print hello world", "Simple Python script"
        )

        assert recommendations["recommended_workflow"] == "legacy"
        assert recommendations["confidence"] <= 0.7

    def test_recommendations_structure(self):
        """Test that recommendations have expected structure"""
        recommendations = get_workflow_recommendations("test request", "test context")

        required_fields = [
            "recommended_workflow",
            "confidence",
            "reasoning",
            "optimizations",
        ]
        for field in required_fields:
            assert field in recommendations

        assert 0.0 <= recommendations["confidence"] <= 1.0
        assert isinstance(recommendations["optimizations"], list)


class TestIntegrationScenarios:
    """Test integration scenarios"""

    def setup_method(self):
        """Set up integration test fixtures"""
        self.mock_provider = Mock(spec=LLMProvider)
        self.mock_provider.model_name = "qwen2.5-coder:7b"

    def test_structured_workflow_full_cycle(self):
        """Test full structured workflow cycle"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=True)

        # Test that all components are properly initialized
        assert manager.structured_workflow is not None
        assert manager.context_manager is not None
        assert manager.performance_validator is not None

        # Test planner retrieval
        planner = manager.get_planner("auto")
        assert planner is not None

        # Test workflow insights
        task_plan = {"description": "test", "mode": "coder"}
        insights = manager.get_workflow_insights(task_plan)
        assert insights["workflow_type"] == "structured"

    def test_legacy_fallback_behavior(self):
        """Test that legacy fallback works properly"""
        manager = WorkflowIntegrationManager(self.mock_provider, use_structured=False)

        # Should only have legacy components
        assert manager.legacy_planner is not None
        assert manager.structured_planner is None

        # Should return legacy planner
        planner = manager.get_planner("auto")
        assert planner == manager.legacy_planner

        # Should return legacy optimization
        optimization = manager.optimize_for_model("qwen2.5-coder:7b")
        assert optimization["optimization"] == "legacy_mode"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
