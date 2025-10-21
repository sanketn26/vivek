# Vivek: v3.0.0 → v4.0.0 Comparison

## Side-by-Side Comparison

### Architecture

#### v3.0.0 (Current)
```
┌─────────────────────────────────────────┐
│           User Request                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      SimpleOrchestrator                 │
│  - Keyword-based task generation        │
│  - Sequential execution                 │
│  - Single LLM provider                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Single LLM Call                 │
│  "Create a function that..."            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Generated Code                 │
│  (no quality check)                     │
│  (no iteration)                         │
└─────────────────────────────────────────┘
```

#### v4.0.0 (Target)
```
┌─────────────────────────────────────────┐
│           User Request                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      DualBrainOrchestrator              │
│  - LLM-based planning                   │
│  - Dependency-aware execution           │
│  - Multi-provider support               │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│ Planner LLM  │  │ Project Context  │
│ (thinking)   │  │ - Languages      │
│              │  │ - Frameworks     │
│ Analyzes     │  │ - File structure │
│ Decomposes   │  │ - Conventions    │
│ Creates plan │  │ - Recent changes │
└──────┬───────┘  └──────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│        Work Items with Dependencies     │
│  1. Create model (coder mode)           │
│  2. Create service (coder mode) ← dep 1 │
│  3. Add tests (sdet mode) ← dep 1,2     │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┴────────────┐
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│ Executor LLM │ ... │ Executor LLM │
│ (coding)     │      │ (coding)     │
│              │      │              │
│ Implements   │      │ Implements   │
│ work item 1  │      │ work item N  │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  ▼
       ┌────────────────────┐
       │   Quality Gate     │
       │   (planner LLM)    │
       │                    │
       │   Score: 0.0-1.0   │
       └────────┬───────────┘
                │
       ┌────────┴─────────┐
       │                  │
       ▼ score >= 0.6     ▼ score < 0.6
┌──────────────┐    ┌──────────────┐
│ Accept       │    │ Iterate      │
│ Final Output │    │ with Feedback│
└──────────────┘    └──────────────┘
```

---

## Feature Comparison

| Feature | v3.0.0 | v4.0.0 |
|---------|--------|--------|
| **Task Decomposition** | Keyword heuristics | LLM-based intelligent planning |
| **Work Item Granularity** | Single task | File-level with dependencies |
| **Execution Modes** | ❌ None | ✅ Coder, SDET, Architect, Peer |
| **Quality Checking** | ❌ No | ✅ Yes, with iteration |
| **LLM Providers** | Ollama only | Ollama, Claude, Sarvam, + more |
| **Dual-Model Support** | ❌ No | ✅ Separate planner/executor |
| **Project Context** | ❌ Minimal | ✅ Rich context awareness |
| **Dependency Resolution** | ❌ No | ✅ Topological sort |
| **Parallel Execution** | ❌ No | ✅ Yes, where possible |
| **Error Recovery** | ❌ Fails fast | ✅ Fallback providers |
| **Prompt Optimization** | ❌ Generic | ✅ Small LLM optimized |
| **Cost Tracking** | ❌ No | ✅ Yes, per request |
| **Streaming Output** | ❌ No | ✅ Optional |
| **Caching** | ❌ No | ✅ LLM response cache |

---

## Code Examples

### Task: "Create a REST API with user authentication"

#### v3.0.0 Behavior

```python
# Simple heuristic matching
if "create" in user_input and "api" in user_input:
    tasks = [
        Task(
            id="task_1",
            description="Create API with authentication"
        )
    ]

# Single LLM call
response = llm.generate(
    "Create a REST API with user authentication"
)

# Returns: One large code block
# No tests, no structure, no validation
```

**Output**: Single file with all code mixed together ❌

---

#### v4.0.0 Behavior

```python
# Planner LLM analyzes request
plan = await planner.decompose_request(
    user_input="Create a REST API with user authentication",
    context=ProjectContext(
        languages=["python"],
        frameworks=["fastapi"],
        file_tree={"src/": {...}}
    )
)

# Returns structured plan
plan.work_items = [
    WorkItem(
        id="item_1",
        mode=WorkItemMode.ARCHITECT,
        file_path="docs/api_design.md",
        description="Design auth API endpoints and models",
        dependencies=[]
    ),
    WorkItem(
        id="item_2",
        mode=WorkItemMode.CODER,
        file_path="src/models/user.py",
        description="Create User model with password hashing",
        dependencies=["item_1"]
    ),
    WorkItem(
        id="item_3",
        mode=WorkItemMode.CODER,
        file_path="src/services/auth_service.py",
        description="Implement AuthService with JWT",
        dependencies=["item_2"]
    ),
    WorkItem(
        id="item_4",
        mode=WorkItemMode.CODER,
        file_path="src/api/auth_router.py",
        description="Create FastAPI router for auth endpoints",
        dependencies=["item_3"]
    ),
    WorkItem(
        id="item_5",
        mode=WorkItemMode.SDET,
        file_path="tests/test_auth.py",
        description="Comprehensive tests for auth flow",
        dependencies=["item_2", "item_3", "item_4"]
    )
]

# Executor implements each item with mode-specific prompts
for item in execution_order:
    result = await executor.execute_work_item(item, context)

# Quality gate evaluates
quality = await quality_service.evaluate(results)
if quality.score < 0.6:
    # Iterate with improvements
    await iterate_with_feedback(quality.feedback)
```

**Output**:
- ✅ Design document
- ✅ Separate model file
- ✅ Service layer
- ✅ API router
- ✅ Comprehensive tests
- ✅ All following FastAPI conventions

---

## Prompt Quality

### v3.0.0 Prompts

```
"Create a REST API with user authentication"
```

**Issues:**
- No context about project
- No structure guidance
- Single monolithic output
- No quality criteria

---

### v4.0.0 Prompts

#### Planner Prompt
```
You are a software architect planning implementation.

Project Context:
- Language: Python
- Framework: FastAPI
- Structure: src/, tests/
- Dependencies: fastapi, sqlalchemy, jwt
- Conventions: Use Pydantic models, type hints, pytest

User Request:
Create a REST API with user authentication

Break into 5-8 file-level work items with:
1. Mode (coder/sdet/architect/peer)
2. Exact file path
3. Clear description
4. Dependencies

Output JSON with work items.
```

#### Executor Prompt (Coder Mode)
```
You are a senior software engineer.

Project Context:
- FastAPI project with SQLAlchemy
- Following PEP 8, type hints required
- Recent changes: Added database models

Task:
File: src/services/auth_service.py
Mode: coder
Status: new

Description:
Implement AuthService with:
- register(email, password) -> User
- login(email, password) -> JWT token
- validate_token(token) -> User

Requirements:
- Use bcrypt for password hashing
- Generate JWT with 24h expiry
- Handle errors gracefully
- Add comprehensive docstrings

Generate complete, production-ready Python code.
```

**Benefits:**
- ✅ Rich context
- ✅ Specific requirements
- ✅ Clear output expectations
- ✅ Quality criteria

---

## Configuration

### v3.0.0 Config

```yaml
# .vivek/config.yml
project_settings:
  name: "My Project"

llm_provider: "ollama"
model: "qwen2.5-coder:7b"
```

**Limitations:**
- Single provider/model
- No customization per task
- No fallbacks
- No quality settings

---

### v4.0.0 Config

```yaml
# .vivek/config.yml
project_settings:
  name: "My FastAPI Project"
  languages: ["python"]
  frameworks: ["fastapi", "sqlalchemy"]

llm_configuration:
  # Planner: optimized for reasoning
  planner:
    provider: "anthropic"
    model: "claude-3-haiku-20240307"
    temperature: 0.3
    max_tokens: 2048

  # Executor: optimized for code generation
  executor:
    provider: "ollama"
    model: "qwen2.5-coder:7b"
    temperature: 0.1
    max_tokens: 4096
    base_url: "http://localhost:11434"

  # Fallback if primary fails
  fallback:
    enabled: true
    provider: "sarvam"
    model: "sarvam-2b-v0.5"

  # Quality settings
  quality_threshold: 0.7
  max_iterations: 2
  enable_quality_gate: true

  # Performance
  enable_cache: true
  cache_ttl: 3600
  max_concurrent_items: 3

# Mode-specific settings
modes:
  coder:
    temperature: 0.1
    includes_tests: true
  sdet:
    temperature: 0.2
    test_coverage_target: 0.8
  architect:
    temperature: 0.3
    include_diagrams: true
  peer:
    temperature: 0.4
    suggestions_count: 3

# Context management
context:
  max_files_in_context: 15
  max_tokens_per_context: 12000
  use_semantic_search: true
```

**Benefits:**
- ✅ Dual-model support
- ✅ Provider flexibility
- ✅ Fallback resilience
- ✅ Quality-driven
- ✅ Mode-specific tuning

---

## Performance Comparison

### v3.0.0 Performance

```
Request: "Create a REST API with auth"

Timeline:
├─ 0s: User request
├─ 2s: Simple heuristic creates 1 task
├─ 5s: Single LLM call starts
├─ 45s: LLM generates large code block
└─ 47s: Returns monolithic output

Result: Single file, untested, no validation
Quality: Inconsistent (depends on LLM mood)
```

---

### v4.0.0 Performance

```
Request: "Create a REST API with auth"

Timeline:
├─ 0s: User request
├─ 2s: Build project context
├─ 8s: Planner analyzes & creates 5 work items
├─ 10s: Start parallel execution (3 concurrent)
│   ├─ 18s: Design doc completed (architect mode)
│   ├─ 35s: User model completed (coder mode)
│   ├─ 42s: Auth service completed (coder mode)
│   ├─ 50s: API router completed (coder mode)
│   └─ 65s: Tests completed (sdet mode)
├─ 70s: Quality evaluation
├─ 75s: Quality score: 0.85 (above threshold)
└─ 75s: Returns structured output

Result: 5 files, all tested, validated
Quality: Consistently high (quality gate enforces)
```

**Improvement:**
- Better quality despite longer time
- Structured output vs monolith
- Includes tests automatically
- Validated before delivery

---

## Token Usage

### v3.0.0 Token Usage

```
Single Request:
├─ Prompt: ~200 tokens (minimal context)
├─ Completion: ~800 tokens (large code block)
└─ Total: ~1,000 tokens

Cost (Claude Haiku): $0.00025
```

---

### v4.0.0 Token Usage

```
Complete Workflow:

Planning Phase:
├─ Context: 1,000 tokens
├─ User request: 100 tokens
├─ Planner output: 500 tokens
└─ Subtotal: 1,600 tokens

Execution Phase (5 work items):
├─ Item 1: 800 tokens (design)
├─ Item 2: 1,200 tokens (model)
├─ Item 3: 1,500 tokens (service)
├─ Item 4: 1,200 tokens (router)
├─ Item 5: 1,800 tokens (tests)
└─ Subtotal: 6,500 tokens

Quality Phase:
├─ Review: 1,200 tokens
└─ Subtotal: 1,200 tokens

Total: ~9,300 tokens

Cost (Mixed):
├─ Planner (Claude): 1,600 tokens × $0.25/MTok = $0.0004
├─ Executor (Ollama): 6,500 tokens × $0 = $0
├─ Quality (Claude): 1,200 tokens × $0.25/MTok = $0.0003
└─ Total: $0.0007

With caching (2nd request):
└─ Total: $0.0002 (70% reduction)
```

**ROI:**
- 10x better output quality
- Only 3x token usage
- Net: Massive value improvement

---

## Developer Experience

### v3.0.0 UX

```bash
$ vivek chat
> Create a REST API with user authentication

Thinking...
[45 seconds later]

Here's your code:
```python
# 200 lines of mixed code
```

> Is this correct? (no way to know)
```

**Pain Points:**
- ❌ No visibility into what's happening
- ❌ Can't pause/resume
- ❌ No incremental output
- ❌ All-or-nothing result

---

### v4.0.0 UX

```bash
$ vivek chat
> Create a REST API with user authentication

🧠 Planning...
├─ Analyzing project structure... ✓
├─ Detecting frameworks... FastAPI ✓
└─ Creating execution plan... ✓

📋 Plan created:
├─ 1. Design auth API (architect mode)
├─ 2. Create User model (coder mode)
├─ 3. Implement AuthService (coder mode)
├─ 4. Add API router (coder mode)
└─ 5. Write tests (sdet mode)

Continue? [Y/n] y

⚙️ Executing work items...
├─ [1/5] ✓ docs/api_design.md (8s)
├─ [2/5] ⏳ src/models/user.py (15s elapsed...)
├─ [3/5] ⏳ src/services/auth_service.py (parallel)
├─ [4/5] ⏳ Queued
└─ [5/5] ⏳ Queued

[2/5] ✓ src/models/user.py completed (25s)
[3/5] ✓ src/services/auth_service.py completed (32s)
[4/5] ✓ src/api/auth_router.py completed (28s)
[5/5] ✓ tests/test_auth.py completed (18s)

✨ Checking quality...
├─ Completeness: 0.90 ✓
├─ Correctness: 0.85 ✓
├─ Best practices: 0.88 ✓
├─ Test coverage: 0.82 ✓
└─ Overall: 0.86 ✓ (above threshold)

✅ Complete! Created 5 files in 1m 15s

Files modified:
├─ docs/api_design.md (new)
├─ src/models/user.py (new)
├─ src/services/auth_service.py (new)
├─ src/api/auth_router.py (new)
└─ tests/test_auth.py (new)

Run tests: pytest tests/test_auth.py
```

**Benefits:**
- ✅ Clear visibility
- ✅ Incremental progress
- ✅ Pause/resume capability
- ✅ Quality confidence
- ✅ Actionable output

---

## Migration Example

### Updating Existing Code

```python
# v3.0.0 - Still works!
from vivek import SimpleOrchestrator, ServiceContainer

container = ServiceContainer({"llm_provider": "ollama"})
orchestrator = SimpleOrchestrator(
    container.get_vivek_application_service()
)

result = orchestrator.process_user_request(
    "Add user authentication"
)

# v4.0.0 - New capabilities
from vivek import DualBrainOrchestrator, ServiceContainer
from pathlib import Path

container = ServiceContainer.from_config(".vivek/config.yml")
orchestrator = DualBrainOrchestrator(
    planner_service=container.get_planner_service(),
    executor_service=container.get_executor_service(),
    quality_service=container.get_quality_service(),
    context_builder=container.get_context_builder()
)

result = await orchestrator.process_request(
    user_input="Add user authentication",
    project_root=Path(".")
)

# Access detailed results
for item in result.work_items:
    print(f"✓ {item.file_path}: {item.status}")

print(f"Quality score: {result.quality_score}")
print(f"Iterations: {result.iterations}")
print(f"Total time: {result.elapsed_time}s")
```

---

## Summary

### v3.0.0 Strengths
- ✅ Clean architecture
- ✅ SOLID principles
- ✅ Easy to understand
- ✅ Fast setup

### v3.0.0 Limitations
- ❌ Naive task decomposition
- ❌ Single monolithic output
- ❌ No quality validation
- ❌ Limited to one LLM

---

### v4.0.0 Improvements
- ✅ Intelligent planning
- ✅ Structured work items
- ✅ Quality-driven iteration
- ✅ Multiple LLM providers
- ✅ Mode-specific execution
- ✅ Project context awareness
- ✅ Dependency resolution
- ✅ Error recovery
- ✅ Cost optimization
- ✅ Better UX

### v4.0.0 maintains v3.0.0 strengths
- ✅ Clean architecture
- ✅ SOLID principles
- ✅ Testable
- ✅ Maintainable

---

## Conclusion

**v3.0.0**: Solid foundation, limited capability
**v4.0.0**: Production-ready, intelligent, optimized

The 12-week roadmap transforms Vivek from a proof-of-concept to a production-grade AI coding assistant that competes with GitHub Copilot while optimizing for small, accessible LLMs.

**Next Step**: Start Week 1 implementation! 🚀

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
