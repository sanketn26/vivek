# Workstream 7: Advanced LangGraph Orchestration

**Timeline**: Week 15-17 (3 weeks)
**Goal**: Implement multi-step decision graphs and complex workflows

**Prerequisites**: Workstreams 1-6 complete

---

## Overview

This workstream replaces the simple linear orchestrator with LangGraph-based decision graphs, enabling conditional branching, parallel execution, and sophisticated workflow management.

### Current Limitations
- Linear execution only (Planning → Execution → Quality)
- No conditional branching
- No parallel execution
- No iterative refinement loops
- No failure recovery strategies

### What LangGraph Enables
- **Conditional Branching**: Route to different executors based on complexity
- **Parallel Execution**: Run multiple tasks simultaneously
- **Iterative Loops**: Retry with feedback when quality fails
- **State Persistence**: Save checkpoints for recovery
- **Human-in-the-Loop**: Pause for user approval
- **Dynamic Routing**: Choose executor based on work item type

### Deliverables
- ✅ LangGraph state schema
- ✅ Multi-step decision graph
- ✅ Conditional routing nodes
- ✅ Parallel execution nodes
- ✅ Feedback loops for quality improvement
- ✅ State persistence and recovery
- ✅ Progress tracking and visualization
- ✅ Error recovery strategies
- ✅ 50+ integration tests

---

## Part 1: LangGraph State Schema

### File: `src/vivek/infrastructure/graph/state.py`

```python
"""LangGraph state definition for Vivek workflow."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Node types in the workflow graph."""
    PLANNING = "planning"
    ROUTER = "router"
    EXECUTOR = "executor"
    QUALITY = "quality"
    FEEDBACK = "feedback"
    RETRY = "retry"
    PARALLEL = "parallel"


@dataclass
class WorkItemExecution:
    """Result of executing a single work item."""
    work_item_id: str
    file_path: str
    success: bool
    code: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    attempts: int = 1
    quality_score: Optional[float] = None


@dataclass
class VivekWorkflowState:
    """Complete state for Vivek workflow graph.
    
    This state persists through all nodes in the graph,
    allowing access to all prior decisions and results.
    """
    # Input
    user_request: str
    project_context: str
    skills: List[str] = field(default_factory=list)
    
    # Planning phase
    plan: Optional[Any] = None
    work_items: List[Any] = field(default_factory=list)
    
    # Execution phase
    executions: List[WorkItemExecution] = field(default_factory=list)
    current_work_item: Optional[Any] = None
    current_execution_index: int = 0
    
    # Quality phase
    quality_scores: List[Dict[str, float]] = field(default_factory=list)
    overall_quality_score: Optional[float] = None
    quality_passed: bool = False
    
    # Iteration tracking
    iteration_count: int = 0
    max_iterations: int = 2
    
    # Feedback and retry
    last_feedback: Optional[str] = None
    failed_items: List[str] = field(default_factory=list)
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    last_error: Optional[str] = None
    
    # Session tracking
    session_id: str = ""
    
    # Metadata
    graph_path: List[str] = field(default_factory=list)  # Track node sequence
    timestamps: Dict[str, float] = field(default_factory=dict)
    
    def add_execution(self, execution: WorkItemExecution):
        """Record a work item execution."""
        self.executions.append(execution)
    
    def mark_node_visited(self, node_name: str):
        """Mark a node as visited in the graph."""
        import time
        self.graph_path.append(node_name)
        self.timestamps[node_name] = time.time()
    
    def get_execution_time(self, node_name: str) -> Optional[float]:
        """Get how long a node took to execute."""
        if node_name not in self.timestamps:
            return None
        
        # Find previous node
        node_index = self.graph_path.index(node_name)
        if node_index == 0:
            return None
        
        prev_node = self.graph_path[node_index - 1]
        return self.timestamps[node_name] - self.timestamps[prev_node]
```

---

## Part 2: LangGraph Graph Definition

### File: `src/vivek/infrastructure/graph/workflow_graph.py`

```python
"""LangGraph workflow definition."""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, List
from vivek.infrastructure.graph.state import VivekWorkflowState, NodeType, WorkItemExecution
from vivek.domain.interfaces.i_planner_service import IPlannerService
from vivek.domain.interfaces.i_executor_service import IExecutorService
from vivek.domain.interfaces.i_quality_service import IQualityService


class VivekWorkflowGraph:
    """Build and execute Vivek workflow as LangGraph."""
    
    def __init__(
        self,
        planner: IPlannerService,
        executor: IExecutorService,
        quality: IQualityService
    ):
        self.planner = planner
        self.executor = executor
        self.quality = quality
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph."""
        workflow = StateGraph(VivekWorkflowState)
        
        # Add nodes
        workflow.add_node("planning", self._node_planning)
        workflow.add_node("router", self._node_router)
        workflow.add_node("execute", self._node_execute)
        workflow.add_node("quality", self._node_quality)
        workflow.add_node("feedback", self._node_feedback)
        workflow.add_node("retry", self._node_retry)
        workflow.add_node("parallel_execute", self._node_parallel_execute)
        
        # Add edges
        workflow.add_edge("START", "planning")
        
        # Planning → Router
        workflow.add_edge("planning", "router")
        
        # Router → Execute or Parallel based on complexity
        workflow.add_conditional_edges(
            "router",
            self._should_parallelize,
            {
                "parallel": "parallel_execute",
                "sequential": "execute"
            }
        )
        
        # Execution paths → Quality
        workflow.add_edge("execute", "quality")
        workflow.add_edge("parallel_execute", "quality")
        
        # Quality → Feedback or End
        workflow.add_conditional_edges(
            "quality",
            self._should_retry,
            {
                "retry": "feedback",
                "end": END
            }
        )
        
        # Feedback → Retry → Router or End
        workflow.add_edge("feedback", "retry")
        workflow.add_edge("retry", "router")
        
        # Set entry point
        workflow.set_entry_point("planning")
        
        return workflow.compile()
    
    async def _node_planning(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Planning node: Decompose request into work items."""
        state.mark_node_visited("planning")
        
        # Augment request with skills if provided
        augmented_request = state.user_request
        if state.skills:
            # TODO: Add skill augmentation
            pass
        
        # Create plan
        plan = await self.planner.create_plan(
            augmented_request,
            state.project_context
        )
        
        state.plan = plan
        state.work_items = plan.work_items
        state.iteration_count += 1
        
        print(f"📋 Planning phase: {len(plan.work_items)} work items")
        
        return {
            "plan": plan,
            "work_items": plan.work_items,
            "current_execution_index": 0
        }
    
    async def _node_router(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Router node: Decide execution strategy."""
        state.mark_node_visited("router")
        
        # Count work items
        item_count = len(state.work_items)
        
        # Simple heuristic: parallelize if >3 independent items
        can_parallelize = item_count > 3 and self._are_items_independent(state.work_items)
        
        print(f"🔀 Router: {'Parallel' if can_parallelize else 'Sequential'} execution")
        
        return {
            "should_parallelize": can_parallelize
        }
    
    async def _node_execute(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Execute node: Sequential work item execution."""
        state.mark_node_visited("execute")
        
        print(f"⚙️  Executing {len(state.work_items)} items sequentially...")
        
        for idx, work_item in enumerate(state.work_items):
            state.current_work_item = work_item
            state.current_execution_index = idx
            
            try:
                result = await self.executor.execute(work_item)
                
                execution = WorkItemExecution(
                    work_item_id=idx,
                    file_path=work_item.file_path,
                    success=result.success,
                    code=result.code if hasattr(result, 'code') else None,
                    errors=result.errors if hasattr(result, 'errors') else []
                )
                
                state.add_execution(execution)
                
                print(f"  {'✅' if result.success else '❌'} {work_item.file_path}")
                
            except Exception as e:
                state.errors.append(str(e))
                state.failed_items.append(work_item.file_path)
                print(f"  ❌ {work_item.file_path}: {e}")
        
        return {
            "executions": state.executions,
            "errors": state.errors,
            "failed_items": state.failed_items
        }
    
    async def _node_parallel_execute(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Parallel execute node: Concurrent execution of independent items."""
        state.mark_node_visited("parallel_execute")
        
        print(f"⚙️  Executing {len(state.work_items)} items in parallel...")
        
        import asyncio
        
        # Execute all items concurrently
        tasks = [
            self.executor.execute(item)
            for item in state.work_items
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for idx, (work_item, result) in enumerate(zip(state.work_items, results)):
            if isinstance(result, Exception):
                execution = WorkItemExecution(
                    work_item_id=idx,
                    file_path=work_item.file_path,
                    success=False,
                    errors=[str(result)]
                )
                state.failed_items.append(work_item.file_path)
            else:
                execution = WorkItemExecution(
                    work_item_id=idx,
                    file_path=work_item.file_path,
                    success=result.success,
                    code=result.code if hasattr(result, 'code') else None,
                    errors=result.errors if hasattr(result, 'errors') else []
                )
            
            state.add_execution(execution)
        
        return {
            "executions": state.executions,
            "failed_items": state.failed_items
        }
    
    async def _node_quality(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Quality node: Evaluate outputs."""
        state.mark_node_visited("quality")
        
        print(f"🔍 Evaluating quality...")
        
        # Collect execution results
        results = [
            type('Result', (), {
                'file_path': e.file_path,
                'success': e.success,
                'code': e.code,
                'errors': e.errors
            })()
            for e in state.executions
        ]
        
        quality_score = await self.quality.evaluate(results)
        
        state.overall_quality_score = quality_score.overall if hasattr(quality_score, 'overall') else 0.0
        state.quality_passed = quality_score.passed if hasattr(quality_score, 'passed') else False
        
        print(f"📊 Quality score: {state.overall_quality_score:.2f}")
        
        return {
            "overall_quality_score": state.overall_quality_score,
            "quality_passed": state.quality_passed
        }
    
    async def _node_feedback(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Feedback node: Generate retry guidance."""
        state.mark_node_visited("feedback")
        
        print(f"💬 Generating feedback for retry...")
        
        feedback = self._generate_feedback(state)
        state.last_feedback = feedback
        
        return {
            "last_feedback": feedback
        }
    
    async def _node_retry(self, state: VivekWorkflowState) -> Dict[str, Any]:
        """Retry node: Update items based on feedback."""
        state.mark_node_visited("retry")
        
        print(f"🔄 Preparing retry with feedback...")
        
        # Augment failed items with feedback
        for idx, item in enumerate(state.work_items):
            if item.file_path in state.failed_items:
                # Add feedback to item description
                if state.last_feedback:
                    item.description = f"{item.description}\n\nFeedback from previous attempt: {state.last_feedback}"
        
        # Reset execution state
        state.executions = []
        state.failed_items = []
        
        return {
            "work_items": state.work_items,
            "executions": []
        }
    
    def _should_parallelize(self, state: VivekWorkflowState) -> str:
        """Decide whether to parallelize execution."""
        return "parallel" if getattr(state, 'should_parallelize', False) else "sequential"
    
    def _should_retry(self, state: VivekWorkflowState) -> str:
        """Decide whether to retry based on quality."""
        if state.quality_passed:
            return "end"
        
        if state.iteration_count >= state.max_iterations:
            return "end"
        
        return "retry"
    
    def _are_items_independent(self, items: List) -> bool:
        """Check if work items are independent."""
        # Simple heuristic: if no item has dependencies, they're independent
        for item in items:
            if hasattr(item, 'dependencies') and item.dependencies:
                return False
        return True
    
    def _generate_feedback(self, state: VivekWorkflowState) -> str:
        """Generate feedback for failing items."""
        if not state.failed_items:
            return "Focus on code quality and testing"
        
        return f"Previous failures: {', '.join(state.failed_items)}. Address root causes."
    
    async def invoke(self, user_request: str, project_context: str = "") -> Dict[str, Any]:
        """Execute the workflow end-to-end."""
        initial_state = VivekWorkflowState(
            user_request=user_request,
            project_context=project_context,
            session_id=self._generate_session_id()
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": final_state.quality_passed,
            "results": [
                {
                    "file_path": e.file_path,
                    "success": e.success,
                    "code": e.code
                }
                for e in final_state.executions
            ],
            "quality_score": final_state.overall_quality_score,
            "iterations": final_state.iteration_count,
            "graph_path": final_state.graph_path,
            "session_id": final_state.session_id
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def visualize(self) -> str:
        """Get ASCII visualization of graph."""
        # Return Mermaid diagram
        return """
        graph TD
            A[Planning] --> B{Router}
            B -->|Sequential| C[Execute]
            B -->|Parallel| D[Parallel Execute]
            C --> E[Quality]
            D --> E
            E --> F{Quality Passed?}
            F -->|Yes| END[End]
            F -->|No<br/>Retry Available| G[Feedback]
            G --> H[Retry]
            H --> B
            F -->|No<br/>Max Retries| END
        """
```

---

## Part 3: Progress Tracking and Visualization

### File: `src/vivek/application/services/workflow_visualizer.py`

```python
"""Visualize workflow progress and execution graph."""

from typing import Dict, Any, List
from vivek.infrastructure.graph.state import VivekWorkflowState
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel


class WorkflowVisualizer:
    """Visualize LangGraph workflow execution."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def display_graph_structure(self, graph) -> None:
        """Display the workflow graph structure."""
        mermaid = graph.visualize()
        self.console.print(Panel(mermaid, title="Workflow Graph"))
    
    def display_execution_progress(self, state: VivekWorkflowState) -> None:
        """Display real-time execution progress."""
        table = Table(title="Execution Progress")
        
        table.add_column("Node", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Time (s)", style="green")
        
        for i, node in enumerate(state.graph_path):
            time_taken = state.get_execution_time(node)
            time_str = f"{time_taken:.2f}" if time_taken else "ongoing"
            
            status = "✅" if i < len(state.graph_path) - 1 else "⏳"
            
            table.add_row(node, status, time_str)
        
        self.console.print(table)
    
    def display_execution_summary(self, result: Dict[str, Any]) -> None:
        """Display summary of execution."""
        summary = f"""
        ✅ Success: {result.get('success')}
        📊 Quality Score: {result.get('quality_score', 'N/A'):.2f}
        🔄 Iterations: {result.get('iterations', 1)}
        📁 Files: {len(result.get('results', []))}
        🗂️  Session: {result.get('session_id')}
        """
        
        self.console.print(Panel(summary, title="Execution Complete"))
    
    def display_execution_details(self, executions: List[Dict]) -> None:
        """Display detailed execution results."""
        table = Table(title="Execution Details")
        
        table.add_column("File", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Lines", style="green")
        
        for exec_item in executions:
            status = "✅" if exec_item.get('success') else "❌"
            lines = len(exec_item.get('code', '').split('\n')) if exec_item.get('code') else 0
            
            table.add_row(
                exec_item.get('file_path', 'unknown'),
                status,
                str(lines)
            )
        
        self.console.print(table)
```

---

## Part 4: Testing Strategy

### File: `tests/integration/test_langgraph_workflow.py`

```python
"""Integration tests for LangGraph workflow."""

import pytest
import asyncio
from vivek.infrastructure.graph.workflow_graph import VivekWorkflowGraph
from vivek.infrastructure.graph.state import VivekWorkflowState


class TestLangGraphWorkflow:
    """Test LangGraph workflow execution."""
    
    @pytest.fixture
    def workflow(self, mock_planner, mock_executor, mock_quality):
        """Create workflow with mocks."""
        return VivekWorkflowGraph(
            planner=mock_planner,
            executor=mock_executor,
            quality=mock_quality
        )
    
    @pytest.mark.asyncio
    async def test_basic_workflow_execution(self, workflow):
        """Test basic workflow from start to end."""
        result = await workflow.invoke("Create a function")
        
        assert "success" in result
        assert "results" in result
        assert "quality_score" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_retry(self, workflow):
        """Test workflow retries on low quality."""
        result = await workflow.invoke("Create API endpoint")
        
        assert result.get("iterations", 1) >= 1
    
    @pytest.mark.asyncio
    async def test_workflow_tracks_node_path(self, workflow):
        """Test that workflow tracks node execution path."""
        result = await workflow.invoke("Create model")
        
        # Should execute at least these nodes
        assert "planning" in result["graph_path"]
        assert "execute" in result["graph_path"] or "parallel_execute" in result["graph_path"]
        assert "quality" in result["graph_path"]
    
    def test_state_transitions(self):
        """Test state transitions through workflow."""
        state = VivekWorkflowState(
            user_request="Test",
            project_context=""
        )
        
        state.mark_node_visited("planning")
        assert "planning" in state.graph_path
        
        state.mark_node_visited("execute")
        assert len(state.graph_path) == 2
```

---

## Part 5: Integration with CLI

### File: `src/vivek/presentation/cli/commands/advanced_chat_command.py`

```python
"""Advanced chat command with LangGraph visualization."""

import typer
from typing import Optional
from pathlib import Path
from vivek.infrastructure.di_container import DIContainer
from vivek.infrastructure.graph.workflow_graph import VivekWorkflowGraph
from vivek.application.services.workflow_visualizer import WorkflowVisualizer


def advanced_chat(
    request: str = typer.Argument(..., help="What to implement"),
    visualize: bool = typer.Option(
        False,
        "--visualize",
        "-v",
        help="Show workflow graph visualization"
    ),
    show_details: bool = typer.Option(
        False,
        "--details",
        "-d",
        help="Show detailed execution trace"
    )
):
    """Chat command with advanced LangGraph features.
    
    Examples:
        vivek advanced-chat "Create API" --visualize
        vivek advanced-chat "Create API" --details
    """
    try:
        container = DIContainer()
        
        # Create workflow
        workflow = VivekWorkflowGraph(
            planner=container.get_planner_service(),
            executor=container.get_executor_service(),
            quality=container.get_quality_service()
        )
        
        visualizer = WorkflowVisualizer()
        
        # Show graph structure if requested
        if visualize:
            visualizer.display_graph_structure(workflow)
        
        # Execute workflow
        import asyncio
        result = asyncio.run(workflow.invoke(request))
        
        # Display results
        if show_details:
            visualizer.display_execution_progress(result)
            visualizer.display_execution_details(result.get('results', []))
        
        visualizer.display_execution_summary(result)
        
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
```

---

## Part 6: Deliverables Checklist

- [ ] LangGraph state schema defined
- [ ] Workflow graph with all nodes implemented
- [ ] Conditional routing working
- [ ] Parallel execution working
- [ ] Feedback loops functional
- [ ] State persistence implemented
- [ ] Progress visualization working
- [ ] CLI integration complete
- [ ] 50+ integration tests passing
- [ ] >85% code coverage

---

## Success Criteria

✅ Complex workflows execute end-to-end
✅ Conditional branching works correctly
✅ Parallel execution improves performance
✅ Feedback loops enable quality improvement
✅ State persists across graph traversal
✅ Progress is visualizable
✅ 50+ integration tests pass
✅ >85% code coverage

---

## Performance Targets

- **Planning**: <5 seconds
- **Sequential Execution**: <30 seconds per 5 items
- **Parallel Execution**: <20 seconds for 5 items (50% improvement)
- **Quality Evaluation**: <5 seconds
- **Total (no retries)**: <40 seconds
