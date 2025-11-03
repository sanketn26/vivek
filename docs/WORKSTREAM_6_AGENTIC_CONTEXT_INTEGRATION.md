# Workstream 6: Agentic Context Integration

**Timeline**: Week 13-14 (2 weeks)
**Goal**: Integrate context management for multi-turn coherence and memory

**Prerequisites**: Workstreams 1-5 complete

---

## Overview

This workstream integrates the refactored agentic_context module into Vivek's core orchestration, enabling persistent memory, hierarchical context tracking, and multi-turn coherence.

### Deliverables
- ✅ ContextWorkflow integration into orchestrator
- ✅ Multi-turn chat session management
- ✅ Session persistence (SQLite)
- ✅ Hierarchical context (Session → Activity → Task)
- ✅ Tag-based context retrieval
- ✅ Semantic search integration
- ✅ Context-aware planning (use previous decisions)
- ✅ Memory of dependencies and decisions
- ✅ 40+ integration tests

### Current Status
- ✅ agentic_context module: Refactored, 117 tests passing
- ⏳ Integration into orchestration: **NOT DONE**
- ⏳ Session persistence: **NOT DONE**
- ⏳ CLI chat loop: **NOT DONE**

---

## Part 1: Context-Aware Orchestrator

### File: `src/vivek/application/orchestrators/context_aware_orchestrator.py`

```python
"""Orchestrator with agentic context integration."""

from typing import Optional, Dict, Any, List
from vivek.domain.interfaces.i_planner_service import IPlannerService
from vivek.domain.interfaces.i_executor_service import IExecutorService
from vivek.domain.interfaces.i_quality_service import IQualityService
from vivek.agentic_context.workflow import ContextWorkflow
from vivek.agentic_context.core.context_manager import ContextManager
from vivek.agentic_context.config import Config


class ContextAwareOrchestrator:
    """Orchestrator that maintains context across requests."""
    
    def __init__(
        self,
        planner: IPlannerService,
        executor: IExecutorService,
        quality: IQualityService,
        context_workflow: ContextWorkflow,
        session_id: Optional[str] = None
    ):
        self.planner = planner
        self.executor = executor
        self.quality = quality
        self.context_workflow = context_workflow
        self.session_id = session_id or self._generate_session_id()
        self.context_manager = None
    
    async def execute_request(
        self,
        user_request: str,
        project_context: str = ""
    ) -> Dict[str, Any]:
        """Execute request with context tracking.
        
        This creates a hierarchical context:
        - Session: Entire conversation
        - Activity: Planning phase, execution phase, etc.
        - Task: Individual work items
        """
        
        # Enter session context
        with self.context_workflow.session(
            session_id=self.session_id,
            ask=user_request,
            plan=""
        ) as session_ctx:
            
            # Activity 1: Planning
            with session_ctx.activity(
                activity_id="planning",
                activity_type="planning",
                actor="planner",
                tags=["planning", "decomposition"]
            ) as planning_activity:
                
                # Retrieve relevant context from previous activities
                previous_context = self._retrieve_previous_context("planning")
                
                # Augment request with previous context
                augmented_request = self._augment_with_context(
                    user_request,
                    previous_context
                )
                
                # Plan with context awareness
                print(f"🧠 Planning (with context)...")
                plan = await self.planner.create_plan(
                    augmented_request,
                    project_context
                )
                
                # Record planning decision
                planning_activity.record_decision(f"Created plan with {len(plan.work_items)} items")
                planning_activity.set_result(f"Plan: {[w.file_path for w in plan.work_items]}")
            
            # Activity 2: Execution
            with session_ctx.activity(
                activity_id="execution",
                activity_type="execution",
                actor="executor",
                tags=["execution", "code_generation"]
            ) as execution_activity:
                
                results = []
                
                for idx, work_item in enumerate(plan.work_items, 1):
                    # Create task context for each work item
                    with execution_activity.task(
                        task_id=f"work_item_{idx}",
                        tags=["work_item", work_item.file_path]
                    ) as task_ctx:
                        
                        # Retrieve context from previous related tasks
                        related_context = self._retrieve_context_for_task(
                            work_item,
                            results
                        )
                        
                        # Augment work item with context
                        augmented_item = self._augment_work_item(
                            work_item,
                            related_context
                        )
                        
                        # Execute
                        print(f"  → {work_item.file_path}")
                        result = await self.executor.execute(augmented_item)
                        results.append(result)
                        
                        # Record outcome
                        task_ctx.record_decision(
                            f"Mode: {work_item.mode}, Status: {'✅ Success' if result.success else '❌ Failed'}"
                        )
                        task_ctx.set_result(f"File: {result.file_path}, Success: {result.success}")
                
                # Record execution activity result
                execution_activity.set_result(f"Executed {len(results)} items")
            
            # Activity 3: Quality Evaluation
            with session_ctx.activity(
                activity_id="quality",
                activity_type="quality_evaluation",
                actor="quality_service",
                tags=["quality", "evaluation"]
            ) as quality_activity:
                
                print(f"🔍 Evaluating quality...")
                quality_score = await self.quality.evaluate(results)
                
                # Record quality findings
                quality_activity.record_decision(
                    f"Quality score: {quality_score.overall:.2f}"
                )
                quality_activity.set_result(
                    f"Quality: {quality_score.overall:.2f}, Passed: {quality_score.passed}"
                )
        
        return {
            "success": quality_score.passed if quality_score else False,
            "results": results,
            "quality_score": quality_score,
            "session_id": self.session_id,
            "files_created": [r.file_path for r in results if r.success]
        }
    
    def _retrieve_previous_context(self, tag: str) -> str:
        """Retrieve relevant context from previous activities."""
        # Use semantic search to find related context
        if not self.context_manager:
            return ""
        
        items = self.context_manager.retrieve(
            query_tags=[tag],
            max_results=5
        )
        
        # Summarize retrieved context
        context = "\n".join([
            f"- {item.get('description', '')}: {item.get('result', '')}"
            for item in items
        ])
        
        return context
    
    def _retrieve_context_for_task(
        self,
        work_item,
        previous_results
    ) -> Dict[str, Any]:
        """Get context relevant to a specific task."""
        return {
            "previous_files": [r.file_path for r in previous_results],
            "previous_decisions": [r for r in previous_results],
            "dependencies": work_item.dependencies if hasattr(work_item, 'dependencies') else []
        }
    
    def _augment_with_context(self, request: str, context: str) -> str:
        """Augment user request with previous context."""
        if not context.strip():
            return request
        
        return f"""{request}

Previous context from this session:
{context}

Use this context to maintain coherence and avoid duplication."""
    
    def _augment_work_item(self, work_item, context: Dict) -> Any:
        """Augment work item with relevant context."""
        # Could add context to work_item description
        # For now, return as-is
        return work_item
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())[:8]
```

---

## Part 2: Session Manager

### File: `src/vivek/application/services/session_manager.py`

```python
"""Manage Vivek sessions with persistence."""

from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import sqlite3


@dataclass
class SessionInfo:
    """Session metadata."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    request_count: int = 0
    file_count: int = 0


class SessionManager:
    """Manage session persistence and retrieval."""
    
    def __init__(self, sessions_dir: Path = None):
        self.sessions_dir = sessions_dir or Path.home() / ".vivek" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.sessions_dir / "sessions.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                last_activity TIMESTAMP,
                request_count INTEGER,
                file_count INTEGER,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                request_id TEXT PRIMARY KEY,
                session_id TEXT,
                request_text TEXT,
                response TEXT,
                timestamp TIMESTAMP,
                quality_score REAL,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str) -> SessionInfo:
        """Create a new session."""
        now = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, created_at, last_activity, request_count, file_count)
            VALUES (?, ?, ?, 0, 0)
        """, (session_id, now, now))
        
        conn.commit()
        conn.close()
        
        return SessionInfo(
            session_id=session_id,
            created_at=now,
            last_activity=now
        )
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve session info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, created_at, last_activity, request_count, file_count
            FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return SessionInfo(
            session_id=row[0],
            created_at=row[1],
            last_activity=row[2],
            request_count=row[3],
            file_count=row[4]
        )
    
    def list_sessions(self, limit: int = 10) -> List[SessionInfo]:
        """List recent sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, created_at, last_activity, request_count, file_count
            FROM sessions
            ORDER BY last_activity DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            SessionInfo(
                session_id=row[0],
                created_at=row[1],
                last_activity=row[2],
                request_count=row[3],
                file_count=row[4]
            )
            for row in rows
        ]
    
    def record_request(
        self,
        session_id: str,
        request_text: str,
        response: str,
        quality_score: Optional[float] = None
    ):
        """Record a request/response in session."""
        import uuid
        
        request_id = str(uuid.uuid4())
        now = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert request
        cursor.execute("""
            INSERT INTO requests (request_id, session_id, request_text, response, timestamp, quality_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (request_id, session_id, request_text, response, now, quality_score))
        
        # Update session
        cursor.execute("""
            UPDATE sessions
            SET last_activity = ?, request_count = request_count + 1
            WHERE session_id = ?
        """, (now, session_id))
        
        conn.commit()
        conn.close()
```

---

## Part 3: Multi-Turn Chat Interface

### File: `src/vivek/presentation/cli/commands/chat_loop_command.py`

```python
"""Interactive chat loop with context persistence."""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from vivek.infrastructure.di_container import DIContainer
from vivek.application.services.session_manager import SessionManager


console = Console()


def chat_loop(
    session_id: Optional[str] = typer.Option(
        None,
        "--session",
        "-s",
        help="Resume existing session ID"
    ),
    project_root: Path = typer.Option(
        ".",
        "--project",
        "-p",
        help="Project root directory"
    )
):
    """Start interactive multi-turn chat session.
    
    Commands:
        /exit - Exit session
        /history - Show session history
        /sessions - List available sessions
        /clear - Clear context
    
    Examples:
        vivek loop                    # New session
        vivek loop --session abc123   # Resume session
    """
    try:
        container = DIContainer()
        session_manager = SessionManager()
        orchestrator = container.get_orchestrator()
        
        # Initialize or resume session
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())[:8]
            session_manager.create_session(session_id)
            console.print(f"[green]✅ New session: {session_id}[/green]")
        else:
            session_info = session_manager.get_session(session_id)
            if not session_info:
                console.print(f"[red]❌ Session not found: {session_id}[/red]")
                raise typer.Exit(1)
            console.print(f"[green]✅ Resumed session: {session_id}[/green]")
            console.print(f"   Previous requests: {session_info.request_count}")
        
        # Chat loop
        while True:
            try:
                # Get user input
                request = Prompt.ask("[bold cyan]You[/bold cyan]")
                
                # Handle commands
                if request.startswith("/"):
                    _handle_command(request, session_id, session_manager)
                    continue
                
                # Execute request
                console.print("[yellow]Processing...[/yellow]")
                
                result = orchestrator.execute_request(request)
                
                # Display results
                console.print(Panel(
                    f"✅ Success: {result.get('success')}\n"
                    f"Quality: {result.get('quality_score', 'N/A')}\n"
                    f"Files: {len(result.get('files_created', []))}",
                    title="Result"
                ))
                
                # Record in session
                session_manager.record_request(
                    session_id,
                    request,
                    str(result),
                    result.get('quality_score')
                )
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type /exit to quit or continue.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")


def _handle_command(command: str, session_id: str, manager: SessionManager):
    """Handle special commands."""
    if command == "/exit":
        console.print("[yellow]Goodbye![/yellow]")
        raise typer.Exit(0)
    
    elif command == "/history":
        session_info = manager.get_session(session_id)
        if session_info:
            console.print(f"[cyan]Session {session_id}:[/cyan]")
            console.print(f"  Created: {session_info.created_at}")
            console.print(f"  Requests: {session_info.request_count}")
            console.print(f"  Files: {session_info.file_count}")
    
    elif command == "/sessions":
        sessions = manager.list_sessions()
        for s in sessions:
            console.print(f"  {s.session_id} - {s.request_count} requests")
    
    elif command == "/clear":
        console.print("[yellow]Context cleared (session continues)[/yellow]")
    
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
```

---

## Part 4: Testing Strategy

### File: `tests/integration/test_context_aware_orchestrator.py`

```python
"""Integration tests for context-aware orchestration."""

import pytest
from vivek.application.orchestrators.context_aware_orchestrator import ContextAwareOrchestrator
from vivek.agentic_context.workflow import ContextWorkflow
from vivek.agentic_context.config import Config


class TestContextAwareOrchestrator:
    """Test context-aware orchestration."""
    
    @pytest.fixture
    def orchestrator(self, mock_planner, mock_executor, mock_quality):
        """Create orchestrator with mocks."""
        workflow = ContextWorkflow()
        return ContextAwareOrchestrator(
            planner=mock_planner,
            executor=mock_executor,
            quality=mock_quality,
            context_workflow=workflow,
            session_id="test_session"
        )
    
    @pytest.mark.asyncio
    async def test_single_request_creates_context(self, orchestrator):
        """Test that a single request creates proper context."""
        result = await orchestrator.execute_request("Create a function")
        
        assert result["session_id"] == "test_session"
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_multiple_requests_maintain_context(self, orchestrator):
        """Test that multiple requests maintain context."""
        # First request
        result1 = await orchestrator.execute_request("Create User model")
        assert result1["success"]
        
        # Second request - should have context from first
        result2 = await orchestrator.execute_request("Create AuthService using User")
        assert result2["success"]
        
        # Both in same session
        assert result1["session_id"] == result2["session_id"]
    
    @pytest.mark.asyncio
    async def test_context_hierarchy(self, orchestrator):
        """Test hierarchical context (Session → Activity → Task)."""
        result = await orchestrator.execute_request("Create API")
        
        # Check that context hierarchy was created
        assert result["session_id"]
        assert "results" in result
```

### File: `tests/unit/application/test_session_manager.py`

```python
"""Tests for session management."""

import pytest
from pathlib import Path
from vivek.application.services.session_manager import SessionManager
import tempfile


class TestSessionManager:
    """Test session persistence."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create session manager."""
        return SessionManager(sessions_dir=temp_dir)
    
    def test_create_session(self, manager):
        """Test creating a session."""
        session = manager.create_session("test_001")
        
        assert session.session_id == "test_001"
        assert session.request_count == 0
    
    def test_retrieve_session(self, manager):
        """Test retrieving a session."""
        manager.create_session("test_001")
        session = manager.get_session("test_001")
        
        assert session is not None
        assert session.session_id == "test_001"
    
    def test_record_request(self, manager):
        """Test recording a request in session."""
        manager.create_session("test_001")
        manager.record_request("test_001", "Create API", "success", 0.95)
        
        session = manager.get_session("test_001")
        assert session.request_count == 1
    
    def test_list_sessions(self, manager):
        """Test listing sessions."""
        manager.create_session("test_001")
        manager.create_session("test_002")
        
        sessions = manager.list_sessions()
        assert len(sessions) >= 2
```

---

## Part 5: Integration Checklist

- [ ] ContextWorkflow integrated into orchestrator
- [ ] SessionManager created with SQLite persistence
- [ ] Multi-turn chat loop implemented
- [ ] Context retrieval working (tag-based and semantic)
- [ ] Context augmentation to planning working
- [ ] Context augmentation to execution working
- [ ] Session history persisted correctly
- [ ] 40+ integration tests passing
- [ ] >85% coverage for new code

---

## Deliverables Summary

### Code Changes
- 1 new orchestrator class (context-aware)
- 1 new session manager service
- 1 new CLI command (chat loop)
- 4 test files with 40+ tests

### Integration Points
- Orchestrator now uses ContextWorkflow
- SessionManager handles persistence
- CLI has new `vivek loop` command
- Context flows through planning and execution

### Success Criteria
✅ Multi-turn sessions work
✅ Context persists across requests
✅ Previous decisions inform future work
✅ Session history accessible
✅ 40+ integration tests pass
✅ >85% code coverage
