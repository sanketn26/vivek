# Vivek Skill-Based Augmentation System

---

## Executive Summary

The Skill-Based Augmentation System is a **context injection framework** that enhances Vivek's planning and execution by applying language-specific patterns and role-specific guidance. Skills don't change Vivek's core workflow—they **amplify and refine** how tasks are decomposed and executed.

### Key Principles
- **Augmentation, Not Classification**: Skills inject guidance into existing workflows, not separate execution paths
- **Language First, Role Second**: Language skills (Python/TypeScript/Go) provide high-ROI, reliable augmentation; role skills provide optional depth
- **Minimal Detection Complexity**: Simple, reliable signals over sophisticated ML-based classification
- **Non-Invasive Integration**: Works with existing Planner/Executor, doesn't replace them

### What Skills Actually Do
1. **Language Skills** inject language-specific patterns into code generation (e.g., Python type hints, Go error handling)
2. **Role Skills** adjust planning depth and considerations (e.g., Architect emphasizes design docs, TestEngineer emphasizes edge cases)
3. **Combined Context** flows through Planner → Executor as augmented prompts

---

## Part 1: Core Concept

### 1.1 What is Skill-Based Augmentation?

**Traditional Approach (No Skills)**:
```
User: "Add user authentication"
↓
Planner: Break into tasks
↓
Executor: Generate code
```

**Augmented Approach (With Skills)**:
```
User: "Add user authentication"
↓
Detect Context: Python + Coder mode
↓
Planner (augmented): "As a Python developer, break into tasks considering:
  - Use type hints
  - Follow PEP 8
  - Include error handling
  - Think about dependencies"
↓
Executor (augmented): "Implement with Python best practices:
  - Use dataclasses for models
  - Async/await for I/O
  - Include docstrings"
```

**The difference**: Same workflow, but **context-aware guidance** improves quality.

### 1.2 The Two-Tier Skill Model

#### Tier 1: Language Skills (High Priority)
**Purpose**: Inject language-specific patterns and idioms

| Language | Augmentation Focus | Detection Confidence |
|----------|-------------------|---------------------|
| **Python** | Type hints, async/await, PEP 8, pythonic patterns | High (file extensions, imports) |
| **TypeScript** | Strict typing, composition, React patterns | High (tsconfig.json, .ts files) |
| **Go** | Goroutines, explicit errors, interfaces | High (go.mod, .go files) |
| **Unknown** | Generic best practices | Fallback |

**Why High Priority**: 
- Detection is reliable (file extensions, config files)
- Guidance has immediate impact (correct syntax, patterns)
- ROI is measurable (code quality, fewer errors)

#### Tier 2: Role Skills (Optional Depth)
**Purpose**: Adjust planning depth and quality considerations

| Role | Planning Augmentation | When to Use |
|------|----------------------|-------------|
| **Coder** | Pragmatic, simple, get-it-done focus | Default for implementation |
| **Architect** | Design-first, scalability, documentation | Greenfield or major refactors |
| **TestEngineer** | Test-first, edge cases, coverage | Quality/testing focus |
| **Debugger** | Systematic investigation, root cause | Fixing issues |
| **CodeReviewer** | Quality standards, improvements | Reviewing existing code |

**Why Optional**: 
- Detection is less reliable (intent-based, ambiguous)
- User can explicitly choose mode
- Guidance is softer (suggestions, not requirements)

### 1.3 Implementation Model

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class LanguageSkill(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    UNKNOWN = "unknown"

class RoleSkill(Enum):
    CODER = "coder"           # Default: pragmatic implementation
    ARCHITECT = "architect"   # Design-focused
    TEST_ENGINEER = "test_engineer"
    DEBUGGER = "debugger"
    CODE_REVIEWER = "code_reviewer"

@dataclass
class SkillContext:
    """Augmentation context for planning and execution"""
    language: LanguageSkill
    role: RoleSkill
    
    # How this context was determined
    language_source: str  # "detected" | "config" | "default"
    role_source: str      # "detected" | "user_choice" | "default"
    
    # Optional: Why these were chosen
    detection_notes: Optional[str] = None
```

---

## Part 2: How Augmentation Works

### 2.1 Detection Strategy

**Language Detection (Automatic, High Confidence)**:
```python
class LanguageDetector:
    """Detect language from project context - file-based, reliable"""
    
    def detect(self, project_context: ProjectContext) -> tuple[LanguageSkill, str]:
        """
        Returns: (language, source)
        
        Detection order:
        1. Check .vivek/config.yml (explicit user preference)
        2. Check file extensions in project
        3. Check config files (pyproject.toml, tsconfig.json, go.mod)
        4. Default to UNKNOWN
        """
        # Check config first
        if project_context.language_preference:
            return (project_context.language_preference, "config")
        
        # Count file extensions
        file_counts = self._count_files_by_extension(project_context.workspace_path)
        
        if file_counts.get('.py', 0) > 0:
            return (LanguageSkill.PYTHON, "detected")
        elif file_counts.get('.ts', 0) > 0 or file_counts.get('.tsx', 0) > 0:
            return (LanguageSkill.TYPESCRIPT, "detected")
        elif file_counts.get('.go', 0) > 0:
            return (LanguageSkill.GO, "detected")
        
        return (LanguageSkill.UNKNOWN, "default")
```

**Role Detection (User-Driven, Optional)**:
```python
class RoleSelector:
    """Simple user selection, no ML magic"""
    
    def select(self, previous_role: Optional[RoleSkill] = None) -> tuple[RoleSkill, str]:
        """
        Returns: (role, source)
        
        Strategy:
        1. If first interaction: Ask user once
        2. If continuing session: Reuse previous role
        3. User can override with --mode flag
        """
        if previous_role:
            return (previous_role, "session_context")
        
        # First interaction: simple selection
        console.print("\n[bold]Working mode:[/bold]")
        console.print("1. 💻 Coder (default - pragmatic implementation)")
        console.print("2. 🏗️  Architect (design-first approach)")
        console.print("3. 🧪 TestEngineer (test-driven development)")
        console.print("4. 🐛 Debugger (systematic investigation)")
        console.print("5. 👀 CodeReviewer (quality review)")
        
        choice = Prompt.ask("Select mode", choices=["1", "2", "3", "4", "5"], default="1")
        
        role_map = {
            "1": RoleSkill.CODER,
            "2": RoleSkill.ARCHITECT,
            "3": RoleSkill.TEST_ENGINEER,
            "4": RoleSkill.DEBUGGER,
            "5": RoleSkill.CODE_REVIEWER,
        }
        
        return (role_map[choice], "user_choice")
```

### 2.2 Guidance Injection Points

**Injection Point 1: Planner Prompt Augmentation**
```python
# BEFORE (no augmentation)
planner_prompt = f"""Break down this user request into 3-5 tasks:
{user_ask}"""

# AFTER (with augmentation)
language_guidance = LANGUAGE_GUIDANCE[skill_context.language]
role_guidance = ROLE_GUIDANCE[skill_context.role]

planner_prompt = f"""You are planning work in {skill_context.language.value}.

Language Context:
{language_guidance}

Role Context:
{role_guidance}

Break down this request into 3-5 tasks:
{user_ask}"""
```

**Injection Point 2: Executor Task Prompts**
```python
# BEFORE
executor_prompt = f"Implement: {task.description}"

# AFTER
executor_prompt = f"""Implement this task in {skill_context.language.value}:
{task.description}

Apply these patterns:
{LANGUAGE_GUIDANCE[skill_context.language]}

Quality standards:
{ROLE_GUIDANCE[skill_context.role]}"""
```

**Injection Point 3: Session Context Storage**
```python
# Store for conversation continuity
with workflow.activity("implementation", metadata={
    "skill_context": skill_context,
    "language": skill_context.language.value,
    "role": skill_context.role.value,
}):
    # Activity execution
    pass
```

### 2.3 Guidance Content (DRY - Define Once)

```python
LANGUAGE_GUIDANCE = {
    LanguageSkill.PYTHON: """
Python Best Practices:
- Use type hints for function signatures
- Follow PEP 8 naming conventions
- Prefer list/dict comprehensions over loops where clear
- Use dataclasses for simple data structures
- Handle exceptions explicitly
- Include docstrings for public functions
- Use async/await for I/O operations
- Organize imports: stdlib, third-party, local
""",
    
    LanguageSkill.TYPESCRIPT: """
TypeScript Best Practices:
- Enable strict mode, avoid 'any' types
- Use interfaces for object shapes
- Prefer const over let, avoid var
- Use composition over inheritance
- Leverage union types and type guards
- Use async/await over raw Promises
- Prefer functional components (React)
- Destructure props and state
""",
    
    LanguageSkill.GO: """
Go Best Practices:
- Explicit error handling (no exceptions)
- Use goroutines for concurrency
- Defer for cleanup operations
- Small, focused interfaces
- Table-driven tests
- Use context for cancellation
- Avoid global state
- Follow effective Go naming conventions
""",
    
    LanguageSkill.UNKNOWN: """
General Best Practices:
- Write clear, readable code
- Handle errors explicitly
- Use meaningful names
- Keep functions focused
- Include tests
- Document complex logic
""",
}

ROLE_GUIDANCE = {
    RoleSkill.CODER: """
Coder Focus:
- Prioritize working code over perfect code
- Keep it simple and readable
- Think about immediate dependencies
- Write code that's easy to debug
- Include basic error handling
""",
    
    RoleSkill.ARCHITECT: """
Architect Focus:
- Design for scalability and maintainability
- Document key design decisions
- Consider failure modes and edge cases
- Think about system boundaries
- Plan for testing and observability
- Explain trade-offs made
""",
    
    RoleSkill.TEST_ENGINEER: """
Test Engineer Focus:
- Think test-first (what to verify?)
- Consider edge cases and failure modes
- Aim for good coverage of critical paths
- Use fixtures and mocks appropriately
- Write clear, maintainable tests
- Include both unit and integration tests
""",
    
    RoleSkill.DEBUGGER: """
Debugger Focus:
- Systematic investigation approach
- Identify root cause, not symptoms
- Add debugging output and logs
- Document the issue and fix
- Suggest prevention mechanisms
- Verify the fix thoroughly
""",
    
    RoleSkill.CODE_REVIEWER: """
Code Reviewer Focus:
- Check for clarity and maintainability
- Verify error handling
- Look for potential bugs
- Suggest improvements
- Ensure tests are adequate
- Consider performance implications
""",
}
```

---

## Part 3: Integration Architecture

### 3.1 Minimal Changes to Existing System

**Current Vivek Flow**:
```
CLI → Orchestrator → Planner → Tasks → Executor → Results
```

**Augmented Flow**:
```
CLI → [Detect Skills] → Orchestrator(+context) → Planner(+guidance) → Tasks → Executor(+guidance) → Results
                ↓
         Store in session
```

**Changes Required**:
1. ✅ CLI: Add skill detection before orchestrator call
2. ✅ Orchestrator: Accept optional `skill_context` parameter
3. ✅ Planner: Inject guidance into prompts
4. ✅ Executor: Inject guidance into task execution
5. ✅ Session: Store skill context for continuity

**Backward Compatibility**: All changes are additive (optional parameters with defaults)

### 3.2 File Structure

```
src/vivek/
├── domain/
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── skill_context.py       # SkillContext dataclass
│   │   ├── language_detector.py   # File-based detection
│   │   ├── role_selector.py       # User selection UI
│   │   └── guidance.py            # LANGUAGE_GUIDANCE, ROLE_GUIDANCE
│   │
│   └── (existing domain models)
│
├── application/
│   ├── orchestrators/
│   │   └── simple_orchestrator.py (MODIFIED - accept skill_context)
│   │
│   ├── services/
│   │   └── vivek_application_service.py (MODIFIED - pass to LLM)
│   │
│   └── skill_augmentation.py     # NEW - coordinates detection + injection
│
├── cli.py (MODIFIED)              # Detect skills, pass to orchestrator
│
└── (existing infrastructure)
```

### 3.3 Code Integration Examples

**CLI Integration**:
```python
# vivek/cli.py (modified)

from vivek.domain.skills import LanguageDetector, RoleSelector, SkillContext
from vivek.application.skill_augmentation import SkillAugmentationService

@cli.command()
@click.option('--mode', type=click.Choice(['coder', 'architect', 'test', 'debug', 'review']))
def chat(mode: Optional[str]):
    """Start chat with skill-based augmentation"""
    
    # Load project context
    project_ctx = ProjectContext.load_from_config()
    
    # Detect language (automatic)
    language_detector = LanguageDetector()
    language, lang_source = language_detector.detect(project_ctx)
    
    # Select role (user-driven or flag)
    role_selector = RoleSelector()
    if mode:
        role = RoleSkill[mode.upper()]
        role_source = "cli_flag"
    else:
        role, role_source = role_selector.select()
    
    # Create skill context
    skill_context = SkillContext(
        language=language,
        role=role,
        language_source=lang_source,
        role_source=role_source,
    )
    
    # Show detected context
    console.print(f"\n🎯 Context: {language.value} + {role.value} mode")
    console.print(f"   (Language: {lang_source}, Role: {role_source})\n")
    
    # Create augmented orchestrator
    orchestrator = SimpleOrchestrator(app_service)
    
    # Chat loop with skill context
    while True:
        user_input = Prompt.ask("You")
        
        result = orchestrator.process_user_request(
            user_input,
            skill_context=skill_context  # NEW PARAMETER
        )
        
        console.print(result)
```

**Orchestrator Integration**:
```python
# vivek/application/orchestrators/simple_orchestrator.py (modified)

class SimpleOrchestrator:
    def process_user_request(
        self,
        user_input: str,
        thread_id: str = "default",
        skill_context: Optional[SkillContext] = None,  # NEW
    ) -> Dict[str, Any]:
        """Process with optional skill augmentation"""
        
        # Generate tasks (with augmented planning if skills provided)
        tasks = self._generate_tasks_from_request(
            user_input,
            skill_context=skill_context  # Pass through
        )
        
        # Execute tasks (with augmented execution)
        for task in tasks:
            response = self.app_service.execute_task_with_llm(
                task,
                skill_context=skill_context  # Pass through
            )
```

**Application Service Integration**:
```python
# vivek/application/services/vivek_application_service.py (modified)

class VivekApplicationService:
    def execute_task_with_llm(
        self,
        task: Task,
        skill_context: Optional[SkillContext] = None  # NEW
    ) -> str:
        """Execute with optional skill guidance"""
        
        prompt = self._build_task_prompt(task, skill_context)  # Augmented
        
        response = self.llm_provider.generate(prompt)
        return response
    
    def _build_task_prompt(
        self,
        task: Task,
        skill_context: Optional[SkillContext] = None
    ) -> str:
        """Build prompt with skill augmentation"""
        
        parts = [f"Execute this task: {task.description}"]
        
        if task.file_path:
            parts.append(f"File: {task.file_path}")
        
        # Inject skill guidance if available
        if skill_context:
            from vivek.domain.skills.guidance import LANGUAGE_GUIDANCE, ROLE_GUIDANCE
            
            parts.append(f"\nLanguage Context ({skill_context.language.value}):")
            parts.append(LANGUAGE_GUIDANCE[skill_context.language])
            
            parts.append(f"\nQuality Standards ({skill_context.role.value}):")
            parts.append(ROLE_GUIDANCE[skill_context.role])
        
        return "\n".join(parts)
```

---

## Part 4: Implementation Roadmap

### Phase 1: Language Skills Only (Week 1-2)
**Goal**: Reliable, high-value augmentation

**Deliverables**:
- LanguageDetector (file-based, config-based)
- LANGUAGE_GUIDANCE dictionary
- CLI integration for language detection
- Planner/Executor prompt injection
- 40+ unit tests for detection + injection

**Success Criteria**:
- Language detected correctly >95% of time
- Guidance visibly affects generated code
- No breaking changes to existing code
- Tests pass, coverage >90%

### Phase 2: Role Skills (Week 2-3)
**Goal**: Optional depth through user-selected modes

**Deliverables**:
- RoleSelector (simple UI)
- ROLE_GUIDANCE dictionary
- CLI flag support (--mode architect)
- Session role persistence
- 30+ tests for role selection + guidance

**Success Criteria**:
- User can select mode easily
- Role guidance affects planning depth
- Mode persists across session
- Can override via CLI flag

### Phase 3: Session Continuity (Week 3-4)
**Goal**: Remember context across conversation

**Deliverables**:
- Store skill_context in session state
- Auto-reuse in same session
- Allow mid-session role switching
- 20+ integration tests

**Success Criteria**:
- Context preserved across requests
- Can switch roles mid-session
- No memory leaks
- End-to-end tests pass

---

## Part 5: Design Principles

### SOLID ✅

**Single Responsibility**:
- LanguageDetector: Only detects language
- RoleSelector: Only handles role selection
- SkillAugmentationService: Only coordinates injection
- No class does more than one thing

**Open/Closed**:
- Add languages by extending LanguageSkill enum + LANGUAGE_GUIDANCE
- Add roles by extending RoleSkill enum + ROLE_GUIDANCE
- No code changes for new guidance content

**Liskov Substitution**:
- skill_context is optional everywhere
- System works identically with or without it
- Augmentation is transparent

**Interface Segregation**:
- Clean interfaces: `detect() → (skill, source)`
- No bloated interfaces

**Dependency Inversion**:
- Orchestrator doesn't know about detection
- Planner doesn't know about storage
- All depend on SkillContext abstraction

### DRY ✅
- One LANGUAGE_GUIDANCE definition
- One ROLE_GUIDANCE definition
- Guidance reused in Planner + Executor
- Zero duplication

### YAGNI ✅

**Implemented**:
- Simple file-based language detection
- User-driven role selection
- Prompt injection
- Session persistence

**NOT Implemented** (future if needed):
- ML-based confidence scoring
- Automatic role inference from user ask
- Cross-language role combinations
- Skill effectiveness metrics
- Custom user-defined skills

---

## Part 6: Success Metrics

### Functional Metrics
- ✅ Language detected correctly in >95% of projects
- ✅ Role selection takes <10 seconds
- ✅ Guidance visibly improves code quality
- ✅ Context persists across session
- ✅ No impact on non-augmented workflows

### Code Quality Metrics
- ✅ 90+ unit tests
- ✅ >90% code coverage
- ✅ All public methods <50 lines
- ✅ Zero breaking changes
- ✅ No exceptions in normal operation

### User Experience Metrics
- ✅ First-time setup: <30 seconds
- ✅ Role selection: Optional, not mandatory
- ✅ Context visible to user (show what was detected)
- ✅ Can override via CLI flags

### Performance Metrics
- ✅ Detection overhead: <10ms
- ✅ Prompt augmentation: <5ms
- ✅ No memory leaks
- ✅ Works with existing mock/real LLM providers

---

## Part 7: Comparison with Original Design

| Aspect | Original "Skills System" | New "Augmentation System" |
|--------|-------------------------|---------------------------|
| **Purpose** | Classify user intent | Inject context into execution |
| **Detection** | Multi-layer ML-style confidence | File-based + user selection |
| **Complexity** | 8 skills, confidence scoring | 2 tiers, simple detection |
| **Integration** | Modifies orchestration flow | Augments existing prompts |
| **UX** | Adaptive confirmation (3 flows) | One-time selection, optional |
| **ROI** | Unclear (classification accuracy) | Clear (code quality improvement) |
| **Risk** | High (brittle detection) | Low (graceful degradation) |
| **Timeline** | 4 weeks, risky | 3 weeks, achievable |

---

## Part 8: Known Limitations & Future Work

### Current Limitations
1. **Language detection is heuristic** - Based on files, not semantic analysis
   - Future: Could integrate with LSP for better accuracy
   
2. **Role selection is manual** - Requires user input
   - Future: Could add optional auto-suggestion based on ask
   
3. **Guidance is static** - Defined once, not adaptive
   - Future: Could learn from user corrections
   
4. **No cross-language projects** - Assumes one primary language
   - Future: Could support polyglot projects with file-level detection

### Future Enhancements (Not in v1)
- Skill effectiveness tracking (did it improve output?)
- Learn user preferences over time
- Project-specific guidance customization
- Integration with language servers for better detection
- A/B testing of guidance effectiveness

---

## Part 9: Getting Started

### For Decision Makers
- **What it does**: Adds language and role context to improve code quality
- **Risk**: Low (optional, additive, backward compatible)
- **Timeline**: 3 weeks (phased, testable)
- **ROI**: Measurable improvement in generated code quality

### For Implementers
- **Start**: Phase 1 (Language skills only)
- **Test**: Each phase independently
- **Integrate**: Minimal changes to existing code
- **Deploy**: Gradual rollout, feature-flagged

### For Users
- **Setup**: `vivek init` auto-detects language
- **Usage**: `vivek chat` or `vivek chat --mode architect`
- **Override**: Can change mode anytime
- **Invisible**: Works without thinking about it

---

## Status: ✅ READY FOR IMPLEMENTATION

**Key Changes from Original Design**:
- ✅ Simplified from "classification" to "augmentation"
- ✅ Removed ML-style confidence scoring
- ✅ Made role selection user-driven, not auto-detected
- ✅ Focused on language skills (high ROI)
- ✅ Reduced complexity, increased clarity

**Start Phase 1 whenever ready.**

---

*Last Updated: October 17, 2025*  
*Vivek Skill-Based Augmentation System - Implementation Guide*
