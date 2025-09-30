# Vivek TODO List

Comprehensive improvement roadmap to make Vivek a truly excellent AI coding assistant.

> **🚨 PRIORITY SHIFT:** LangGraph integration is now the #1 priority as it solves multiple critical issues simultaneously (iteration, state management, persistence, error handling) and provides a solid foundation for all other features.

---

## 🔥 Critical Foundation (Must-Have)

### 1. Integrate LangGraph for Multi-Agent Orchestration ⭐ **NEW #1 PRIORITY**
**Priority:** Critical (Highest)
**Status:** Not Started
**Impact:** Solves Tasks #2, #4, #5, #12 automatically + provides foundation for all features
**Location:** New module `vivek/core/langgraph_orchestrator.py`

**Why This is Now #1:**
LangGraph provides the architectural foundation that makes everything else easier and better:
- ✅ **Replaces 200+ lines** of manual orchestration with declarative graph
- ✅ **Built-in iteration** with conditional edges (solves TODO #2)
- ✅ **Automatic state management** with checkpointing (solves TODO #4)
- ✅ **Retry policies** and error handling (solves TODO #5)
- ✅ **Event streaming** for progress (solves TODO #12)
- ✅ **Human-in-the-loop** for file operations
- ✅ **Time-travel debugging** with LangSmith
- ✅ **Fastest framework** with lowest latency

**Key Benefits:**
- **Proven architecture:** Used in production by many companies
- **Maintainability:** Graph-based is easier to understand than imperative code
- **Extensibility:** Adding new nodes/agents is trivial
- **Observability:** LangSmith provides full tracing
- **Best practices:** Built-in patterns for multi-agent systems

**Tasks:**
- [ ] Add dependencies: `langgraph>=0.1.0`, `langchain-core>=0.2.0`, `langgraph-checkpoint-sqlite>=1.0.0`
- [ ] Create `vivek/core/langgraph_orchestrator.py` with StateGraph implementation
- [ ] Define `VivekState` TypedDict for shared state across nodes
- [ ] Implement nodes: `planner_node`, `executor_node`, `reviewer_node`
- [ ] Add conditional edges for iteration logic (quality_score < 0.6)
- [ ] Integrate SqliteSaver for persistent sessions (`.vivek/checkpoints.db`)
- [ ] Add streaming events for progress indicators
- [ ] Implement human-in-the-loop interrupts for file edits
- [ ] Create backward compatibility layer with existing orchestrator
- [ ] Add `--engine` flag to cli.py (choose legacy vs langgraph)
- [ ] Migrate tests to work with graph-based orchestration
- [ ] Add LangSmith integration for observability (optional)

**Graph Architecture:**
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing_extensions import TypedDict

class VivekState(TypedDict):
    user_input: str
    task_plan: dict
    executor_output: str
    review_result: dict
    iteration_count: int
    mode: str
    context: dict
    final_response: str

# Build graph
workflow = StateGraph(VivekState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("reviewer", reviewer_node)

# Linear flow with conditional iteration
workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    should_iterate,  # Check quality_score and iteration_count
    {"iterate": "executor", "finish": END}
)

# Compile with persistence
checkpointer = SqliteSaver.from_conn_string(".vivek/checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)
```

**Session Management:**
```python
# Each conversation gets a thread_id
async def process_request(self, user_input: str, thread_id: str = "default"):
    config = {"configurable": {"thread_id": thread_id}}

    # Streaming events for progress
    async for event in self.app.astream_events(
        {"user_input": user_input},
        config=config
    ):
        if event["event"] == "on_chain_start":
            print(f"🔄 {event['name']}")

    return final_state["final_response"]
```

**Files to Create:**
- `vivek/core/langgraph_orchestrator.py` - Main StateGraph implementation
- `vivek/core/graph_nodes.py` - Node functions (planner, executor, reviewer)
- `vivek/core/graph_state.py` - State definitions and helpers
- `tests/test_langgraph_orchestrator.py` - Graph tests
- `tests/test_graph_nodes.py` - Individual node tests

**Files to Modify:**
- `vivek/cli.py` - Add `--engine` flag, support both orchestrators
- `pyproject.toml` - Add langgraph dependencies

**Migration Strategy:**
1. **Week 1:** Build LangGraph orchestrator alongside existing code
2. **Week 2:** Test thoroughly, add feature parity
3. **Week 3:** Switch default to LangGraph, keep legacy as fallback
4. **Week 4:** Deprecate legacy orchestrator

**Success Metrics:**
- [ ] All existing tests pass with new orchestrator
- [ ] Iteration loop works automatically (quality-based)
- [ ] Sessions persist across restarts
- [ ] Progress indicators show real-time updates
- [ ] Response latency improves by 10-20%

**Related Reading:**
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)
- [LangGraph vs LangChain 2025](https://xenoss.io/blog/langchain-langgraph-llamaindex-llm-frameworks)

---

### 2. Implement File Operations with LangChain Tools
**Priority:** Critical
**Status:** Not Started
**Location:** New module `vivek/tools/file_tools.py`
**Depends On:** Task #1 (LangGraph integration)

Currently Vivek has no ability to read/write/edit files in the project. With LangGraph, we can implement these as tools that the executor can use.

**Tasks:**
- [ ] Create LangChain tools using `@tool` decorator for file operations
- [ ] Implement `read_file` tool with .gitignore respect (pathspec)
- [ ] Implement `write_file` tool with backup creation
- [ ] Implement `edit_file` tool with diff preview (human-in-the-loop)
- [ ] Implement `search_files` tool (by name pattern)
- [ ] Implement `grep_files` tool (by content)
- [ ] Add `list_directory` tool for exploration
- [ ] Integrate tools with executor node in graph
- [ ] Add interrupt before file edits for user approval

**LangChain Tool Example:**
```python
from langchain.tools import tool
from typing import Annotated

@tool
def read_file(path: Annotated[str, "Path to file relative to project root"]) -> str:
    """Read a file from the project, respecting .gitignore"""
    # Implementation with pathspec filtering
    return file_contents

@tool
def edit_file(
    path: Annotated[str, "Path to file"],
    old_content: Annotated[str, "Content to replace"],
    new_content: Annotated[str, "New content"]
) -> str:
    """Edit a file with preview. Requires human approval."""
    # Show diff, wait for approval (interrupt)
    return "Edit applied"
```

**Graph Integration:**
```python
# Add tool executor node
from langgraph.prebuilt import ToolExecutor

tools = [read_file, write_file, edit_file, search_files, grep_files]
tool_executor = ToolExecutor(tools)

# Executor can use tools
workflow.add_node("tool_executor", tool_executor)
workflow.add_edge("executor", "tool_executor")

# Interrupt before file edits
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["tool_executor"]  # User approval needed
)
```

**Files to Create:**
- `vivek/tools/__init__.py`
- `vivek/tools/file_tools.py` - File operation tools
- `vivek/tools/search_tools.py` - Search and grep tools
- `tests/test_file_tools.py`

**Related:**
- README.md:304 mentions "File Operations (smart editing, project analysis)"
- pathspec>=0.11.0 already in dependencies for .gitignore support
- LangGraph human-in-the-loop for approval workflow

---

### 3. Complete Iteration Loop ✅ **SOLVED BY LANGGRAPH (#1)**
**Priority:** ~~Critical~~ → **Handled by LangGraph**
**Status:** Will be built into graph
**Location:** LangGraph conditional edges

~~Line 173 says "Could implement iteration here"~~ - This is now automatic with LangGraph conditional edges.

**LangGraph Implementation (from Task #1):**
```python
def should_iterate(state: VivekState) -> str:
    """Conditional edge - automatic iteration logic"""
    review = state["review_result"]
    if review["needs_iteration"] and review["quality_score"] < 0.6:
        if state["iteration_count"] < 3:  # Max 3 attempts
            return "iterate"
    return "finish"

workflow.add_conditional_edges(
    "reviewer",
    should_iterate,
    {"iterate": "executor", "finish": END}
)
```

**Automatic Features:**
- ✅ Re-execution when quality_score < 0.6
- ✅ Feedback passed in state to executor
- ✅ Max iteration limit (3) built-in
- ✅ Iteration count tracked in state
- ✅ Progress shown via event streaming
- ✅ Configurable thresholds in state

**No separate implementation needed - built into Task #1**

---

### 4. Project Context Awareness
**Priority:** Critical
**Status:** Not Started
**Location:** New module `vivek/core/project_analyzer.py`
**Synergy with:** Task #1 (LangGraph) - analyzer becomes a tool

SessionContext doesn't actually analyze the project - it just tracks interactions. With LangGraph, we can create analysis tools.

**Tasks:**
- [ ] Create `ProjectAnalyzer` class to understand project structure
- [ ] Parse project files to build file tree and relationships
- [ ] Detect language/framework from actual files (not just config)
- [ ] Build symbol index (classes, functions, imports) for better `relevant_files` detection
- [ ] Identify entry points, main modules, test directories
- [ ] Track dependencies (from requirements.txt, package.json, go.mod, etc.)
- [ ] Cache analysis results for performance
- [ ] Re-analyze on file changes (integrate with watchdog)

**Files to Create:**
- `vivek/core/project_analyzer.py`
- `tests/test_project_analyzer.py`

**Integration:**
- SessionContext should use ProjectAnalyzer on initialization
- Planner should use project analysis for better relevant_files suggestions
- File operations should trigger incremental re-analysis

---

### 5. Persistent Session State ✅ **SOLVED BY LANGGRAPH (#1)**
**Priority:** ~~High~~ → **Handled by LangGraph**
**Status:** Built into SqliteSaver checkpointer
**Location:** LangGraph SqliteSaver (`.vivek/checkpoints.db`)

~~No session persistence~~ - LangGraph provides automatic state checkpointing with SqliteSaver.

**LangGraph Implementation (from Task #1):**
```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Automatic persistence
checkpointer = SqliteSaver.from_conn_string(".vivek/checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)

# Each conversation gets a thread_id
config = {"configurable": {"thread_id": "my-session-123"}}

# Resume conversations automatically
result = await app.ainvoke({"user_input": "..."}, config=config)
```

**Automatic Features:**
- ✅ Auto-save after every node execution
- ✅ Resume conversations by thread_id
- ✅ Full state history with time-travel
- ✅ Checkpoint cleanup utilities built-in
- ✅ Multiple concurrent sessions supported

**Additional Tasks (Nice-to-have):**
- [ ] Add `/sessions list` command to show all thread_ids
- [ ] Add `/sessions switch <id>` to change active session
- [ ] Add session naming/tagging in UI
- [ ] Export session to markdown for sharing

**No major implementation needed - built into Task #1**

---

### 6. Better Error Handling (Enhanced by LangGraph)
**Priority:** High
**Status:** Needs Improvement
**Location:** Multiple files + LangGraph retry policies
**Synergy with:** Task #1 (LangGraph provides retry/fallback)

Generic error handling needs improvement. LangGraph provides built-in retry policies, but we still need custom exceptions.

**Tasks:**
- [ ] Create custom exception classes in `vivek/core/exceptions.py`
- [ ] Specific handling for Ollama connection failures (with retry logic)
- [ ] Model not found errors with suggestions to pull models
- [ ] Graceful degradation when models are slow (timeout handling)
- [ ] Better JSON parsing error messages with example of expected format
- [ ] Configuration validation errors with specific fixes
- [ ] Network errors with offline mode fallback
- [ ] Add structured error logging

**Exception Classes to Create:**
```python
class VivekError(Exception): pass
class OllamaConnectionError(VivekError): pass
class ModelNotFoundError(VivekError): pass
class ConfigurationError(VivekError): pass
class FileOperationError(VivekError): pass
class JSONParseError(VivekError): pass
```

**Files to Modify:**
- `vivek/llm/models.py` (OllamaProvider error handling)
- `vivek/core/orchestrator.py` (pipeline error handling)
- `vivek/cli.py` (user-facing error messages)

---

## 🎯 Core Features (High Priority)

### 6. Implement `vivek review` Command
**Priority:** High
**Status:** Not Started (referenced in README but doesn't exist)
**Location:** `vivek/cli.py` (new command)

Referenced in README.md:218-220 but doesn't exist.

**Tasks:**
- [ ] Add `@cli.command()` for `review` in cli.py
- [ ] Implement `--mode` flag (sdet, architect, coder)
- [ ] Implement `--files` flag (staged, modified, all, or specific paths)
- [ ] Implement `--scope` flag (changed, all)
- [ ] Add output formats: text, JSON, SARIF (for CI/CD integration)
- [ ] Integrate with git to get staged/modified files
- [ ] Create `CodeReviewer` class in `vivek/core/reviewer.py`
- [ ] Support reviewing specific line ranges
- [ ] Generate review reports with severity levels

**Example Usage:**
```bash
vivek review --mode=sdet --files=staged
vivek review --mode=architect --scope=changed --output=json
vivek review --files=auth.py,models.py
```

**Files to Create:**
- `vivek/core/reviewer.py`
- `tests/test_reviewer.py`

---

### 7. Implement `vivek analyze` Command
**Priority:** High
**Status:** Not Started (referenced in README but doesn't exist)
**Location:** `vivek/cli.py` (new command)

Referenced in README.md:222-241 but doesn't exist.

**Tasks:**
- [ ] Add `@cli.command()` for `analyze` in cli.py
- [ ] Analyze project architecture and structure
- [ ] Detect anti-patterns (god objects, circular dependencies, etc.)
- [ ] Generate architecture documentation
- [ ] Implement `--check` flag for pattern validation
- [ ] Implement `--output` flag (markdown, json, html)
- [ ] Create architecture diagrams (text-based with ASCII art)
- [ ] Identify technical debt areas
- [ ] Suggest refactoring opportunities

**Example Usage:**
```bash
vivek analyze --mode=architect --check=patterns
vivek analyze --output=markdown > ARCHITECTURE.md
vivek analyze --focus=dependencies
```

**Files to Create:**
- `vivek/core/analyzer.py`
- `tests/test_analyzer.py`

---

### 8. Web Search Integration
**Priority:** Medium-High
**Status:** Not Started (Roadmap v0.2.0)
**Location:** New module `vivek/plugins/search.py`

Listed in roadmap v0.2.0 and README.md:303.

**Tasks:**
- [ ] Design plugin system for search providers
- [ ] Implement DuckDuckGo search provider (no API key needed)
- [ ] Implement Google search provider (with API key)
- [ ] Implement StackOverflow specific search
- [ ] Integrate search results into context (add to SessionContext)
- [ ] Smart decision on when to search (error messages, unknown libraries, etc.)
- [ ] Add `search_enabled` configuration option (already in config but not used)
- [ ] Cache search results to avoid duplicate queries
- [ ] Add `/search <query>` command for manual searches

**Files to Create:**
- `vivek/plugins/__init__.py`
- `vivek/plugins/search.py`
- `vivek/plugins/providers/duckduckgo.py`
- `vivek/plugins/providers/stackoverflow.py`
- `tests/test_search.py`

**Configuration:**
- Use existing `search_enabled` preference in config.yml

---

### 9. Advanced Context Condensation Strategies
**Priority:** Medium-High
**Status:** Needs Enhancement (basic implementation exists)
**Location:** `vivek/core/orchestrator.py` (SessionContext)

Current condensation is very basic - just keeps last 10 interactions.

**Tasks:**
- [ ] Implement embeddings-based similarity search (use sentence-transformers)
- [ ] Find relevant past interactions by semantic similarity
- [ ] Cluster related work sessions
- [ ] Better project_summary generation using planner model (not just string concat)
- [ ] Implement smart context window management (keep most relevant, not just recent)
- [ ] Add importance scoring for interactions
- [ ] Preserve critical decisions even if old
- [ ] Periodic full context regeneration from condensed history

**Dependencies to Add:**
- `sentence-transformers` or `openai` (for embeddings)

**Files to Modify:**
- `vivek/core/orchestrator.py` (SessionContext class)
- Add `vivek/core/embeddings.py` for vector operations

---

### 10. Git Integration Improvements
**Priority:** Medium
**Status:** Minimal (GitPython is dependency but barely used)
**Location:** New module `vivek/core/git_integration.py`

GitPython>=3.1.0 is a dependency but barely used.

**Tasks:**
- [ ] Create `GitManager` class to wrap GitPython operations
- [ ] Understand current branch, recent commits for context
- [ ] Analyze git blame for file context (who changed what, when)
- [ ] Generate commit messages from staged changes
- [ ] Create PRs with proper descriptions (GitHub/GitLab CLI integration)
- [ ] Show diff in context for better understanding
- [ ] Integrate with review command (review PR, review commit)
- [ ] Track file history to understand evolution
- [ ] Suggest related files based on git history

**Files to Create:**
- `vivek/core/git_integration.py`
- `tests/test_git_integration.py`

**Commands to Add:**
- `vivek commit` - Generate commit message from staged changes
- `vivek pr` - Create pull request with AI-generated description

---

## 💎 User Experience (Medium Priority)

### 11. Configuration Validation
**Priority:** Medium
**Status:** Not Started
**Location:** `vivek/cli.py` (init and chat commands)

No validation of config files on load.

**Tasks:**
- [ ] Create `ConfigValidator` class
- [ ] Validate vivek.md/config.yml structure on load
- [ ] Check if configured models exist in Ollama
- [ ] Provide helpful error messages for misconfigurations
- [ ] Suggest fixes (e.g., "Model not found. Run: ollama pull qwen2.5-coder:7b")
- [ ] Validate ignored_paths patterns
- [ ] Check for required fields
- [ ] Warn on deprecated configuration options
- [ ] Add `vivek config validate` command

**Files to Create:**
- `vivek/core/config_validator.py`
- `tests/test_config_validator.py`

---

### 12. Progress Indicators
**Priority:** Medium
**Status:** Minimal (basic spinner exists)
**Location:** `vivek/cli.py` (chat_loop function)

Long operations have minimal feedback.

**Tasks:**
- [ ] Show detailed model thinking time
- [ ] Display what step planner/executor is on
- [ ] Show token usage stats per request
- [ ] Add estimated time remaining for long operations
- [ ] Show progress bars for model downloads
- [ ] Display streaming responses (character by character)
- [ ] Add debug mode with verbose logging
- [ ] Show context size and condensation stats

**Rich Components to Use:**
- `rich.progress.Progress`
- `rich.live.Live` for real-time updates
- `rich.tree.Tree` for showing pipeline steps

**Files to Modify:**
- `vivek/cli.py` (enhance chat_loop)
- `vivek/core/orchestrator.py` (add progress callbacks)

---

### 13. Conversation History UI
**Priority:** Medium
**Status:** Not Started
**Location:** `vivek/cli.py` (new commands)

No way to view or search past interactions.

**Tasks:**
- [ ] Add `/history` command to show recent interactions
- [ ] Add `/history search <query>` for searching conversations
- [ ] Add `/history export` to save to markdown
- [ ] Show condensed vs full history views
- [ ] Add pagination for long histories
- [ ] Color-code by mode (peer, architect, sdet, coder)
- [ ] Show timestamps and quality scores
- [ ] Add `/replay <interaction_id>` to re-run past requests

**Files to Modify:**
- `vivek/cli.py` (add history commands to handle_command)
- `vivek/core/orchestrator.py` (add history retrieval methods)

---

### 14. Smart Model Selection
**Priority:** Medium
**Status:** Not Started (always uses configured models)
**Location:** `vivek/llm/models.py` and orchestrator

Always uses statically configured models.

**Tasks:**
- [ ] Auto-select faster models for simple tasks
- [ ] Implement task complexity estimator
- [ ] Suggest model upgrades when quality is consistently poor
- [ ] Support multiple executor models (specialist per mode)
- [ ] Add model performance tracking
- [ ] Implement model fallback chain (primary -> secondary -> tertiary)
- [ ] Add `--fast` flag to prefer speed over quality
- [ ] Add `--quality` flag to prefer best models

**Model Tiers:**
- **Fast:** codellama:7b-code, deepseek-coder:1.3b
- **Balanced:** qwen2.5-coder:7b, deepseek-coder:6.7b
- **Quality:** qwen2.5-coder:32b, codellama:34b-instruct

**Files to Modify:**
- `vivek/llm/models.py` (add ModelSelector class)
- `vivek/core/orchestrator.py` (use dynamic model selection)

---

### 15. Interactive Setup Improvements
**Priority:** Low-Medium
**Status:** Basic (exists but minimal)
**Location:** `vivek/cli.py` (setup command)

`vivek setup` is basic - just checks Ollama and downloads one model.

**Tasks:**
- [ ] Test models after download with sample prompts
- [ ] Benchmark models on user's hardware (tokens/sec)
- [ ] Suggest optimal models based on available RAM
- [ ] Show disk space requirements before download
- [ ] Parallel model downloads
- [ ] Model quality comparison table
- [ ] Save benchmark results for future reference
- [ ] Setup wizard for first-time users

**Files to Modify:**
- `vivek/cli.py` (enhance setup command)
- Add `vivek/core/benchmarks.py` for model testing

---

## 🧪 Quality & Testing (Medium Priority)

### 16. Improve Test Coverage
**Priority:** Medium
**Status:** Basic tests exist (733 lines total code)
**Location:** `tests/` directory

Tests exist but likely incomplete.

**Tasks:**
- [ ] Mock Ollama calls properly (use pytest-mock)
- [ ] Test full orchestration pipeline end-to-end
- [ ] Test all context condensation strategies
- [ ] Add integration tests with real models (marked as `@pytest.mark.slow`)
- [ ] Test all CLI commands with click.testing.CliRunner
- [ ] Test error conditions and edge cases
- [ ] Add property-based tests with hypothesis
- [ ] Achieve >80% code coverage
- [ ] Add coverage reporting to CI/CD

**Coverage Goals:**
- `vivek/llm/models.py`: 90%+
- `vivek/core/orchestrator.py`: 85%+
- `vivek/cli.py`: 70%+

**Dependencies to Add:**
- `pytest-mock>=3.10.0`
- `hypothesis>=6.0.0`
- `pytest-cov>=4.0.0`

---

### 17. Add Telemetry (Optional, Privacy-Preserving)
**Priority:** Low
**Status:** Not Started
**Location:** New module `vivek/core/telemetry.py`

No visibility into usage patterns.

**Tasks:**
- [ ] Track mode usage, common patterns (locally only)
- [ ] Measure response times, quality scores
- [ ] Track iteration frequency
- [ ] Log error rates by type
- [ ] Session duration and interaction counts
- [ ] Model performance metrics
- [ ] Privacy-preserving (all data stays local in `.vivek/telemetry.db`)
- [ ] Add `/stats` command to view analytics
- [ ] Optional export for sharing with community (anonymized)

**Files to Create:**
- `vivek/core/telemetry.py`
- `tests/test_telemetry.py`

**Storage:**
- SQLite database in `.vivek/telemetry.db`

---

### 18. Validation of LLM Outputs
**Priority:** Medium
**Status:** Basic fallbacks exist
**Location:** `vivek/llm/models.py` (_parse_task_plan, _parse_review)

JSON parsing has basic fallbacks but could be more robust.

**Tasks:**
- [ ] Retry on malformed JSON (up to 3 attempts with prompt fixes)
- [ ] Validate schema before parsing (use pydantic)
- [ ] Log parsing failures for debugging
- [ ] Add prompt engineering to improve JSON consistency
- [ ] Implement response validation middleware
- [ ] Add schema examples in prompts
- [ ] Fall back to text parsing if JSON fails repeatedly
- [ ] Track JSON parse success rate in telemetry

**Dependencies to Add:**
- `pydantic>=2.0.0` for schema validation

**Files to Modify:**
- `vivek/llm/models.py` (enhance parsing methods)

---

## 🚀 Advanced Features (Lower Priority)

### 19. Cloud Fallback
**Priority:** Low (Roadmap v0.3.0)
**Status:** Not Started
**Location:** New module `vivek/llm/cloud_providers.py`

Roadmap v0.3.0 feature.

**Tasks:**
- [ ] OpenAI API integration (GPT-4, GPT-3.5)
- [ ] Anthropic API integration (Claude)
- [ ] Smart routing based on task complexity
- [ ] Cost tracking per session
- [ ] Add `fallback_enabled` configuration option (already in config but not used)
- [ ] Automatic fallback on local model failure
- [ ] Cost estimation before cloud requests
- [ ] Monthly spending limits

**Files to Create:**
- `vivek/llm/cloud_providers.py`
- `vivek/llm/providers/openai_provider.py`
- `vivek/llm/providers/anthropic_provider.py`
- `tests/test_cloud_providers.py`

**Dependencies to Add:**
- `openai>=1.0.0`
- `anthropic>=0.7.0`

---

### 20. Multi-File Operations
**Priority:** Medium
**Status:** Not Started (depends on #1)
**Location:** Extends `vivek/core/file_operations.py`

Currently only single-file focus.

**Tasks:**
- [ ] Refactorings across multiple files
- [ ] Consistent naming changes (rename class, update all references)
- [ ] Code generation that spans files
- [ ] Import management across files
- [ ] Move functionality between files
- [ ] Extract class/function to new file
- [ ] Merge related files

**Depends On:**
- Task #1 (File Operations)
- Task #3 (Project Context Awareness)

---

### 21. IDE Integrations
**Priority:** Low (Roadmap v0.4.0)
**Status:** Not Started
**Location:** New repositories/packages

Roadmap v0.4.0 feature.

**Tasks:**
- [ ] Design LSP (Language Server Protocol) for editor integration
- [ ] Create VS Code extension
- [ ] Create Vim/Neovim plugin
- [ ] Create IntelliJ plugin
- [ ] Implement hover tooltips
- [ ] Implement code actions (quick fixes)
- [ ] Inline AI suggestions
- [ ] Sidebar chat interface

**Repositories to Create:**
- `vivek-vscode` (TypeScript)
- `vivek-vim` (VimScript/Lua)
- `vivek-intellij` (Kotlin/Java)
- `vivek-lsp` (Python)

---

### 22. Team Features
**Priority:** Low (Roadmap v0.3.0)
**Status:** Not Started
**Location:** New module `vivek/core/team.py`

Roadmap v0.3.0 feature.

**Tasks:**
- [ ] Shared project configurations (team vivek.md templates)
- [ ] Team coding standards enforcement
- [ ] Shared condensed context across team
- [ ] Team model preferences
- [ ] Collaborative sessions
- [ ] Code review workflows
- [ ] Onboarding automation

**Files to Create:**
- `vivek/core/team.py`
- `tests/test_team.py`

---

### 23. Performance Optimizations
**Priority:** Low
**Status:** Not Started
**Location:** Multiple files

Various performance improvements.

**Tasks:**
- [ ] Parallel planner/executor model loading at startup
- [ ] Response streaming for faster perceived performance
- [ ] Model caching and warming
- [ ] Lazy loading of heavy dependencies
- [ ] Context caching between requests
- [ ] Incremental file indexing (not full re-scan)
- [ ] Async file operations
- [ ] Connection pooling for Ollama requests

**Files to Modify:**
- `vivek/core/orchestrator.py` (async improvements)
- `vivek/llm/models.py` (caching, streaming)

---

### 24. Documentation Generation
**Priority:** Low
**Status:** Not Started
**Location:** New module `vivek/core/doc_generator.py`

**Tasks:**
- [ ] Generate API docs from code (docstrings)
- [ ] Create README from project analysis
- [ ] Generate architecture diagrams from codebase
- [ ] Create user guides for detected features
- [ ] Generate changelog from git history
- [ ] Create onboarding documentation
- [ ] API documentation in OpenAPI/Swagger format

**Commands:**
- `vivek docs generate`
- `vivek docs readme`
- `vivek docs api`

**Files to Create:**
- `vivek/core/doc_generator.py`
- `tests/test_doc_generator.py`

---

### 25. Testing Automation Enhancements
**Priority:** Low
**Status:** Not Started
**Location:** New module `vivek/core/test_generator.py`

**Tasks:**
- [ ] Generate tests for uncovered code
- [ ] Test data generation (fixtures, mocks)
- [ ] Mutation testing integration
- [ ] Visual regression testing
- [ ] Performance test generation
- [ ] Fuzz testing automation
- [ ] Test maintenance (update failing tests)

**Commands:**
- `vivek test generate <file>`
- `vivek test coverage`
- `vivek test mutate`

**Files to Create:**
- `vivek/core/test_generator.py`
- `tests/test_test_generator.py`

---

## 📊 Summary (REVISED with LangGraph)

**Total Tasks:** 25 major features with 200+ sub-tasks

**🎯 MAJOR CHANGE:** LangGraph integration (#1) now solves multiple critical tasks automatically:
- ✅ Task #3: Iteration loop (conditional edges)
- ✅ Task #5: Session persistence (SqliteSaver)
- ✅ Task #12: Progress indicators (event streaming)
- 🔄 Task #6: Enhanced error handling (retry policies)

**New Priority Breakdown:**
- 🔥 **Critical:** 1 task - LangGraph integration (solves 4 others)
- 🔥 **Critical (Depends on #1):** 3 tasks - File ops, Project context, Error handling
- 🎯 **High:** 5 tasks - Core features (review, analyze, git, etc.)
- 💎 **Medium:** 8 tasks - User experience and quality
- 🚀 **Low:** 7 tasks - Advanced features

**Massive Wins from LangGraph:**
1. **Iteration loop** - Built-in with conditional edges ✅
2. **Session persistence** - SqliteSaver automatic ✅
3. **Progress tracking** - Event streaming ✅
4. **State management** - Graph state ✅
5. **Human-in-the-loop** - Interrupt nodes ✅
6. **Observability** - LangSmith integration ✅
7. **Error resilience** - Retry policies ✅

**Dependencies Simplified:**
- **Before:** Everything depended on building custom orchestration
- **After:** Everything builds on proven LangGraph foundation

**Roadmap Acceleration:**
- v0.1.5 (Foundation): LangGraph + Tools (Weeks 1-2)
- v0.2.0 (Context Master): Tasks #4, #7, #8, #9 (Weeks 3-6)
- v0.3.0 (Cloud Hybrid): Tasks #19, #22 (Weeks 7-10)
- v0.4.0 (Enterprise Ready): Tasks #21, #24 (Weeks 11+)

---

## 🎯 REVISED Implementation Order (LangGraph First!)

### **Phase 0: Foundation Reset (Weeks 1-2)** ⭐ HIGHEST PRIORITY
1. **LangGraph Integration (#1)** - Replaces manual orchestration
   - Week 1: Build StateGraph, migrate nodes, add checkpointing
   - Week 2: Testing, docs, CLI integration with `--engine` flag
   - **Impact:** Solves 4 critical tasks immediately

### **Phase 1: Essential Tools (Weeks 3-4)**
Now we can build on solid LangGraph foundation:
1. **File Operations (#2)** - LangChain tools for executor
2. **Project Context (#4)** - Analysis tools for planner
3. **Better Error Handling (#6)** - Custom exceptions + retry policies

### **Phase 2: Core Commands (Weeks 5-7)**
With tools in place, add user-facing features:
1. **`vivek review` command (#7)** - Code review workflows
2. **`vivek analyze` command (#8)** - Architecture analysis
3. **Configuration validation (#11)** - Better UX
4. **Git integration (#10)** - Commit messages, PR descriptions

### **Phase 3: Intelligence Layer (Weeks 8-10)**
Make Vivek smarter:
1. **Web search integration (#9)** - Augmented responses
2. **Advanced context strategies (#10)** - Embeddings
3. **Smart model selection (#14)** - Dynamic routing
4. **Conversation history UI (#13)** - Better UX

### **Phase 4: Advanced Features (Weeks 11+)**
1. **Cloud fallback (#19)** - OpenAI/Anthropic
2. **Multi-file operations (#20)** - Complex refactoring
3. **Team features (#22)** - Collaboration
4. **IDE integrations (#21)** - VS Code, Vim

---

## 🚀 Quick Start for Contributors

**Want to help? Start here:**

1. **Week 1-2:** Implement LangGraph orchestrator (Task #1)
   - Highest impact, unblocks everything
   - Clear architecture, well-documented
   - Immediate wins: iteration, persistence, streaming

2. **Week 3-4:** Add file operation tools (Task #2)
   - Enables actual code editing
   - Builds on LangChain tool pattern
   - Human-in-the-loop already solved by LangGraph

3. **Week 5+:** Pick any feature you're passionate about
   - All building on solid foundation
   - No complex orchestration to worry about
   - Just implement nodes/tools and wire them up

**Key Insight:** LangGraph changes everything. What was 25 separate complex tasks is now:
- 1 foundational task (LangGraph)
- 24 features that build on it naturally

This is a **10x improvement** in development velocity and code quality.