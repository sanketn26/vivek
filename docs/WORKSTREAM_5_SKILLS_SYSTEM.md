# Workstream 5: Skills System

**Timeline**: Week 7-12 (6 weeks)
**Goal**: Add specialized domain expertise via Skills composition

**Prerequisites**: Workstreams 1-4 complete

---

## Overview

This workstream implements the Skills System - transforming Vivek from a general-purpose assistant into a specialized multi-disciplinary professional platform with composable expertise.

### Strategic Enhancement Plan
Based on impact/effort analysis, Workstream 5 is restructured with prioritized sub-workstreams:

| Priority | Sub-Workstream | Approach | Impact | Effort |
|----------|---|---|---|---|
| 🔴 High | **5.1** | Skill Prompts | Immediate quality boost | Low |
| 🔴 High | **5.2** | Skill Executors | Structural control over pipeline | Medium |
| 🟡 Medium | **5.3** | Skill Phases | Better multi-turn reasoning | Medium |
| 🟡 Medium | **5.4** | Workflow DAG | Multi-skill orchestration | High |
| 🟢 Low | **5.5** | Enforced Rubrics | Validation loops | High |

### Core Deliverables
- ✅ Skill domain models (Skill, Trait, QualityRubric)
- ✅ Skill registry and discovery system
- ✅ YAML-based skill definitions (7 core skills)
- ✅ Skill composition and sequencing
- ✅ SkillManager service
- ✅ CLI integration with --skills flag
- ✅ Quality evaluation per skill
- ✅ Extensibility framework for custom skills
- ✅ 90+ unit tests + integration tests
- ✅ Complete documentation

### Impact
- **Before**: Generic code generation
- **After**: Expert-level, domain-specific output with measurable quality per skill

---

## Sub-Workstreams

### 5.1: Skill Prompts System (HIGHEST PRIORITY - Week 7)
**Priority**: 🔴 High | **Impact**: Immediate quality boost | **Effort**: Low

Implement context-aware prompts that inject skill-specific instructions directly into LLM prompts.

#### Objectives
- Create skill-specific system prompts for each domain
- Build prompt template injection system
- Integrate with existing Planner and Executor
- Provide immediate quality improvements without architectural changes

#### Key Components
1. **Prompt Template Library**
   - File: `src/vivek/skills/prompts/templates.py`
   - Role-specific system prompts (coder, architect, test_engineer, reviewer)
   - Language-specific prompts (python, typescript, go)
   - Composable prompt fragments

2. **Skill Prompt Injector**
   - File: `src/vivek/skills/prompts/skill_prompt_injector.py`
   - Merge skill prompts into execution context
   - Maintain prompt ordering for optimal effect
   - Handle conflicting instructions gracefully

3. **LLM Parameter Tuning Per Skill**
   - Temperature adjustments (0.1 for strict, 0.3 for balanced, 0.5 for creative)
   - Top-p and top-k configurations
   - Model selection per skill (qwen2.5-coder for code, etc.)

#### Implementation Files
```
src/vivek/skills/
├── prompts/
│   ├── __init__.py
│   ├── templates.py          # System prompt templates
│   ├── fragments.py          # Reusable prompt fragments
│   ├── skill_prompt_injector.py
│   ├── templates/
│   │   ├── coder.prompt
│   │   ├── architect.prompt
│   │   ├── test_engineer.prompt
│   │   ├── code_reviewer.prompt
│   │   ├── python.prompt
│   │   ├── typescript.prompt
│   │   └── go.prompt
```

#### Success Criteria
- [ ] 7 core skill prompts defined and tested
- [ ] Prompt injection passes 30+ tests
- [ ] Quality metrics improve 15-25% immediately
- [ ] No breaking changes to existing pipeline

---

### 5.2: Skill Executors (HIGHEST PRIORITY - Week 8-9)
**Priority**: 🔴 High | **Impact**: Structural control | **Effort**: Medium

Implement specialized executor classes that control the execution behavior per skill.

#### Objectives
- Create SkillExecutor base class
- Implement skill-specific executor variants
- Enable skill-aware execution with custom behavior
- Maintain compatibility with existing executor infrastructure

#### Key Components
1. **Base Skill Executor**
   - File: `src/vivek/llm/executors/skill_executor.py`
   - Abstract base for skill-specific behavior
   - Hooks for pre/post-processing
   - Skill trait application

2. **Specialized Executors**
   - File: `src/vivek/llm/executors/specialized/`
   - `coder_executor.py` - Pragmatic implementation focus
   - `architect_executor.py` - Design-first approach
   - `test_engineer_executor.py` - Test-first approach
   - `code_reviewer_executor.py` - Quality focus

3. **Skill Executor Factory**
   - File: `src/vivek/llm/executors/skill_executor_factory.py`
   - Dynamic executor selection based on active skills
   - Composition of multiple executors

#### Implementation Architecture
```
BaseExecutor
    ↓
SkillExecutor (abstract)
    ├── CoderExecutor
    │   └── Pragmatic implementation patterns
    ├── ArchitectExecutor
    │   └── Design-first with documentation
    ├── TestEngineerExecutor
    │   └── Test-first with coverage
    └── CodeReviewerExecutor
        └── Quality metrics and feedback
```

#### Behavior Customization Points
```python
class SkillExecutor:
    def pre_execution_hook(self, context)
    def transform_prompt(self, prompt, traits) 
    def post_execution_hook(self, result)
    def evaluate_output(self, output, rubric)
    def get_mode_specific_instructions(self) -> str
```

#### Success Criteria
- [ ] SkillExecutor base class fully implemented
- [ ] 4+ specialized executors working
- [ ] Executor composition functional
- [ ] 40+ executor-specific tests passing
- [ ] Backward compatibility maintained

---

### 5.3: Skill Phases System (MEDIUM PRIORITY - Week 9-10)
**Priority**: 🟡 Medium | **Impact**: Better multi-turn reasoning | **Effort**: Medium

Implement multi-phase execution where skills are applied sequentially in reasoning phases.

#### Objectives
- Define execution phases (Planning → Analysis → Implementation → Review)
- Map skills to phases
- Enable iterative refinement across phases
- Support skill-specific phase customization

#### Key Components
1. **Phase Definitions**
   - File: `src/vivek/domain/models/skill_phase.py`
   - SkillPhase model with phase-specific traits
   - Phase sequencing and dependencies
   - Phase exit criteria

2. **Phase Executor**
   - File: `src/vivek/core/langgraph_orchestrator_phases.py`
   - LangGraph nodes for each phase
   - Skill activation per phase
   - Cross-phase context propagation

3. **Phase Routing**
   - File: `src/vivek/core/phase_router.py`
   - Determine which skills apply to which phases
   - Conditional phase execution
   - Phase result aggregation

#### Phase Architecture
```
Phase 1: Planning (Architect skill active)
  ↓ [design document + requirements]
Phase 2: Analysis (Test Engineer skill active)
  ↓ [test strategy + coverage plan]
Phase 3: Implementation (Coder skill active)
  ↓ [implementation code]
Phase 4: Review (Code Reviewer skill active)
  ↓ [reviewed + refined code]
```

#### Success Criteria
- [ ] Phase model fully defined
- [ ] All phases implemented and testable
- [ ] Skill-to-phase mapping works correctly
- [ ] 35+ phase-specific tests passing
- [ ] Multi-turn reasoning improved

---

### 5.4: Workflow DAG Orchestration (MEDIUM PRIORITY - Week 10-11)
**Priority**: 🟡 Medium | **Impact**: Multi-skill orchestration | **Effort**: High

Implement directed acyclic graph (DAG) for complex multi-skill workflows.

#### Objectives
- Model workflows as DAGs with skill nodes
- Support parallel skill execution where safe
- Enable dynamic DAG generation from skill composition
- Provide visual workflow representation

#### Key Components
1. **Workflow DAG Model**
   - File: `src/vivek/domain/models/workflow_dag.py`
   - DAG node types (SkillNode, ControlNode, DataNode)
   - Edge definitions with data flow
   - Cycle detection and validation

2. **DAG Executor**
   - File: `src/vivek/core/dag_executor.py`
   - Traverse DAG respecting dependencies
   - Handle parallel execution where possible
   - Aggregate results from multiple paths

3. **DAG Visualizer**
   - File: `src/vivek/presentation/dag_visualizer.py`
   - Generate Mermaid DAG diagrams
   - Export to GraphViz format
   - Interactive workflow explorer

#### Example DAG Structure
```
Input Request
    ↓
[Architect Skill] ← (planning phase)
    ↓
[Coder Skill] ← (implementation phase)
   ├→ [Python Skill]
   ├→ [TypeScript Skill]
   └→ [Go Skill]
    ↓
[Test Engineer Skill] ← (test phase)
    ↓
[Code Reviewer Skill] ← (review phase)
    ↓
Output Code
```

#### Success Criteria
- [ ] DAG model complete and validated
- [ ] Parallel execution functional
- [ ] DAG visualizer working
- [ ] 45+ DAG-specific tests passing
- [ ] Workflow definitions shareable

---

### 5.5: Enforced Quality Rubrics (LOW PRIORITY - Week 11-12)
**Priority**: 🟢 Low | **Impact**: Validation loops | **Effort**: High

Implement automated quality validation and iterative refinement based on rubrics.

#### Objectives
- Create skill-specific quality metrics
- Build evaluation agents using LLM
- Implement feedback loops for quality improvement
- Track quality metrics across iterations

#### Key Components
1. **Quality Rubric Engine**
   - File: `src/vivek/domain/services/rubric_evaluator.py`
   - LLM-based rubric evaluation
   - Scoring and feedback generation
   - Rubric customization per project

2. **Feedback Loop Orchestrator**
   - File: `src/vivek/core/feedback_loop_orchestrator.py`
   - Detect quality gaps
   - Route to appropriate skill for refinement
   - Track improvement iterations

3. **Quality Metrics Dashboard**
   - File: `src/vivek/presentation/quality_dashboard.py`
   - Real-time quality scoring
   - Trend analysis
   - Comparative metrics

#### Quality Evaluation Flow
```
Generated Artifact
    ↓
[Evaluate Against Rubric]
    ├→ ✅ Score ≥ threshold → Accept
    └→ ❌ Score < threshold → Feedback Loop
         ↓
    [Identify Deficiency]
         ↓
    [Route to Skill]
         ↓
    [Apply Refinement]
         ↓
    [Re-evaluate]
```

#### Success Criteria
- [ ] Rubric evaluator fully functional
- [ ] Feedback loops working
- [ ] Quality improvements measurable
- [ ] 40+ rubric evaluation tests passing
- [ ] Optional (can be disabled)

---

## Implementation Timeline

### Week 7: Skill Prompts (5.1) - Quick Win
- Day 1-2: Design prompt template system
- Day 3-4: Implement 7 core skill prompts
- Day 5: Integration testing + refinement

### Week 8-9: Skill Executors (5.2) - Structural
- Day 1-2: Design executor architecture
- Day 3-4: Implement 4+ specialized executors
- Day 5-8: Integration + full testing
- Day 9-10: Executor composition

### Week 9-10: Skill Phases (5.3) - Orchestration
- Day 1-2: Phase model design
- Day 3-5: LangGraph phase nodes
- Day 6-7: Phase routing logic
- Day 8-9: Integration testing

### Week 10-11: Workflow DAG (5.4) - Advanced
- Day 1-3: DAG model + validation
- Day 4-6: DAG executor implementation
- Day 7-8: Visualization layer
- Day 9-10: Integration + optimization

### Week 11-12: Quality Rubrics (5.5) - Optional Polish
- Day 1-3: Rubric evaluation engine
- Day 4-6: Feedback loop orchestration
- Day 7-8: Quality dashboard
- Day 9-10: Polish + documentation

---

## Part 1: Domain Models

### File: `src/vivek/domain/models/skill.py`

```python
"""Skill domain models following SOLID principles."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class SkillType(Enum):
    """Skill classification."""
    LANGUAGE = "language"  # Python, TypeScript, Go
    ROLE = "role"          # Coder, Architect, TestEngineer, etc.


class LanguageSkill(Enum):
    """Language expertise areas."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"


class RoleSkill(Enum):
    """Professional role expertise."""
    CODER = "coder"
    ARCHITECT = "architect"
    TEST_ENGINEER = "test_engineer"
    CODE_REVIEWER = "code_reviewer"


@dataclass
class Trait:
    """Individual characteristic that drives behavior.
    
    Examples:
    - "use_type_hints": For Python language skill
    - "focus_documentation": For Architect role
    - "rigorous_testing": For TestEngineer role
    """
    name: str
    description: str
    value: Any  # Can be bool, str, int, dict
    impact_area: str  # "prompt", "model", "quality_eval"


@dataclass
class QualityRubric:
    """Criteria for evaluating work quality per skill."""
    skill_id: str
    criteria: List[str]  # e.g., ["follows_pep8", "includes_docstrings"]
    weight_per_criterion: Dict[str, float]  # Importance weights
    min_score: float = 0.75  # Minimum passing score
    
    def evaluate(self, submission: str, llm_evaluator) -> float:
        """Evaluate submission against rubric."""
        # Placeholder - will use LLM for evaluation
        pass


@dataclass
class Skill:
    """A skill representing expertise in a specific domain.
    
    Skills are composable - multiple skills can be activated together.
    Each skill brings traits that influence planning and execution.
    """
    id: str
    name: str
    skill_type: SkillType
    description: str
    
    # Traits that make this skill unique
    traits: List[Trait] = field(default_factory=list)
    
    # How quality is measured
    quality_rubric: Optional[QualityRubric] = None
    
    # LLM behavior customization
    llm_temperature: float = 0.3
    llm_model_preference: str = "qwen2.5-coder:7b"
    
    # Compatibility
    compatible_skills: List[str] = field(default_factory=list)
    incompatible_skills: List[str] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    
    def is_compatible_with(self, other_skill: 'Skill') -> bool:
        """Check if this skill can be composed with another."""
        if other_skill.id in self.incompatible_skills:
            return False
        if self.compatible_skills and other_skill.id not in self.compatible_skills:
            return False
        return True
    
    def merge_traits_with(self, other_skill: 'Skill') -> List[Trait]:
        """Combine traits from multiple skills for composition."""
        merged = self.traits + other_skill.traits
        # Deduplicate by name, keeping first occurrence
        seen = set()
        result = []
        for trait in merged:
            if trait.name not in seen:
                result.append(trait)
                seen.add(trait.name)
        return result
```

### File: `src/vivek/domain/models/skill_composition.py`

```python
"""Skill composition - combining skills in sequences."""

from dataclasses import dataclass
from typing import List
from vivek.domain.models.skill import Skill


@dataclass
class SkillComposition:
    """Ordered sequence of skills to be applied together.
    
    Example: [architect, coder, test_engineer, code_reviewer]
    Each skill builds on the previous one.
    """
    skills: List[Skill]
    name: str = ""
    description: str = ""
    
    def validate(self) -> tuple[bool, str]:
        """Validate that skills are compatible in this order."""
        if not self.skills:
            return False, "No skills in composition"
        
        for i in range(len(self.skills) - 1):
            current = self.skills[i]
            next_skill = self.skills[i + 1]
            
            if not current.is_compatible_with(next_skill):
                return False, f"{current.id} is incompatible with {next_skill.id}"
        
        return True, "Valid composition"
    
    def get_merged_traits(self) -> List:
        """Get all traits from all skills in order."""
        all_traits = []
        for skill in self.skills:
            all_traits.extend(skill.traits)
        return all_traits
    
    def get_execution_sequence(self) -> List[str]:
        """Return skills in execution order."""
        return [skill.id for skill in self.skills]
```
```

---

## Part 2: Infrastructure - Skill Discovery & Loading

### File: `src/vivek/infrastructure/skills/skill_registry.py`

```python
"""Skill registry - discover and manage available skills."""

from typing import Dict, List, Optional
from vivek.domain.models.skill import Skill, SkillType
from pathlib import Path
import json


class SkillRegistry:
    """Registry of all available skills."""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._load_builtin_skills()
    
    def register_skill(self, skill: Skill) -> None:
        """Register a new skill."""
        if skill.id in self.skills:
            raise ValueError(f"Skill {skill.id} already registered")
        self.skills[skill.id] = skill
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        return self.skills.get(skill_id)
    
    def list_skills(self, skill_type: Optional[SkillType] = None) -> List[Skill]:
        """List all skills, optionally filtered by type."""
        if skill_type:
            return [s for s in self.skills.values() if s.skill_type == skill_type]
        return list(self.skills.values())
    
    def discover_recommended_skills(
        self,
        language: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Skill]:
        """Recommend skills based on language and role.
        
        Example:
            discover_recommended_skills(language="python", role="architect")
            → [PythonSkill, ArchitectSkill, CodeReviewerSkill]
        """
        recommended = []
        
        if language:
            lang_skill = self.get_skill(language.lower())
            if lang_skill:
                recommended.append(lang_skill)
        
        if role:
            role_skill = self.get_skill(role.lower())
            if role_skill:
                recommended.append(role_skill)
        
        return recommended
    
    def _load_builtin_skills(self) -> None:
        """Load built-in skills from YAML."""
        from vivek.infrastructure.skills.skill_loader import SkillLoader
        loader = SkillLoader()
        
        # Load from src/vivek/skills/ directory
        skills_dir = Path(__file__).parent.parent.parent / "skills"
        for skill_file in skills_dir.glob("*.yaml"):
            try:
                skill = loader.load_from_file(skill_file)
                self.register_skill(skill)
            except Exception as e:
                print(f"Warning: Failed to load skill {skill_file}: {e}")
```

### File: `src/vivek/infrastructure/skills/skill_loader.py`

```python
"""Load skills from YAML definitions."""

import yaml
from pathlib import Path
from typing import Dict, Any
from vivek.domain.models.skill import Skill, SkillType, Trait, QualityRubric


class SkillLoader:
    """Load skill definitions from YAML files."""
    
    def load_from_file(self, filepath: Path) -> Skill:
        """Load a skill from YAML file."""
        with open(filepath) as f:
            data = yaml.safe_load(f)
        return self._parse_skill_data(data)
    
    def load_from_dict(self, data: Dict[str, Any]) -> Skill:
        """Load a skill from dictionary."""
        return self._parse_skill_data(data)
    
    def _parse_skill_data(self, data: Dict[str, Any]) -> Skill:
        """Parse skill data structure."""
        # Parse traits
        traits = []
        for trait_data in data.get("traits", []):
            trait = Trait(
                name=trait_data["name"],
                description=trait_data["description"],
                value=trait_data.get("value"),
                impact_area=trait_data.get("impact_area", "prompt")
            )
            traits.append(trait)
        
        # Parse quality rubric
        rubric_data = data.get("quality_rubric")
        quality_rubric = None
        if rubric_data:
            quality_rubric = QualityRubric(
                skill_id=data["id"],
                criteria=rubric_data.get("criteria", []),
                weight_per_criterion=rubric_data.get("weights", {}),
                min_score=rubric_data.get("min_score", 0.75)
            )
        
        # Create skill
        skill = Skill(
            id=data["id"],
            name=data["name"],
            skill_type=SkillType[data["type"].upper()],
            description=data["description"],
            traits=traits,
            quality_rubric=quality_rubric,
            llm_temperature=data.get("llm_temperature", 0.3),
            llm_model_preference=data.get("llm_model_preference", "qwen2.5-coder:7b"),
            compatible_skills=data.get("compatible_skills", []),
            incompatible_skills=data.get("incompatible_skills", []),
            version=data.get("version", "1.0"),
            tags=data.get("tags", [])
        )
        
        return skill
```

---

## Part 3: Skill YAML Definitions

### File: `src/vivek/skills/python.yaml`

```yaml
id: python
name: Python Language Skill
type: language
description: |
  Pythonic code generation with type hints, PEP 8 compliance,
  and idiomatic patterns.

traits:
  - name: use_type_hints
    description: Include type hints for all functions
    value: true
    impact_area: prompt
  
  - name: follow_pep8
    description: Follow PEP 8 style guide
    value: true
    impact_area: prompt
  
  - name: use_dataclasses
    description: Use dataclasses for models
    value: true
    impact_area: prompt
  
  - name: async_support
    description: Use async/await for I/O operations
    value: true
    impact_area: prompt

quality_rubric:
  criteria:
    - has_type_hints
    - follows_pep8
    - includes_docstrings
    - handles_errors
    - uses_modern_python
  weights:
    has_type_hints: 0.25
    follows_pep8: 0.20
    includes_docstrings: 0.20
    handles_errors: 0.20
    uses_modern_python: 0.15
  min_score: 0.80

llm_temperature: 0.2
llm_model_preference: qwen2.5-coder:7b

compatible_skills:
  - coder
  - architect
  - test_engineer
  - code_reviewer

tags:
  - language
  - python
  - type-safe
```

### File: `src/vivek/skills/architect.yaml`

```yaml
id: architect
name: Architect Role Skill
type: role
description: |
  System design focus with emphasis on scalability,
  documentation, and long-term maintainability.

traits:
  - name: design_first
    description: Focus on design before implementation
    value: true
    impact_area: prompt
  
  - name: document_decisions
    description: Include architectural decision records
    value: true
    impact_area: prompt
  
  - name: scalability_focus
    description: Consider scalability in all designs
    value: true
    impact_area: prompt
  
  - name: include_diagrams
    description: Include architecture diagrams in documentation
    value: true
    impact_area: prompt

quality_rubric:
  criteria:
    - clear_design_rationale
    - scalability_considered
    - documentation_complete
    - diagrams_provided
    - maintainability_high
  weights:
    clear_design_rationale: 0.25
    scalability_considered: 0.25
    documentation_complete: 0.20
    diagrams_provided: 0.15
    maintainability_high: 0.15
  min_score: 0.80

llm_temperature: 0.3
llm_model_preference: qwen2.5-coder:7b

compatible_skills:
  - python
  - typescript
  - go
  - coder
  - test_engineer
  - code_reviewer

incompatible_skills: []

tags:
  - role
  - architecture
  - design
```

### File: `src/vivek/skills/test_engineer.yaml`

```yaml
id: test_engineer
name: Test Engineer Role Skill
type: role
description: |
  Test-driven development with emphasis on comprehensive
  coverage, edge cases, and quality metrics.

traits:
  - name: test_first
    description: Write tests before implementation
    value: true
    impact_area: prompt
  
  - name: comprehensive_coverage
    description: Aim for >90% code coverage
    value: true
    impact_area: prompt
  
  - name: edge_case_focus
    description: Identify and test edge cases
    value: true
    impact_area: prompt
  
  - name: performance_testing
    description: Include performance benchmarks
    value: true
    impact_area: prompt

quality_rubric:
  criteria:
    - tests_comprehensive
    - coverage_high
    - edge_cases_covered
    - test_quality_high
    - documentation_clear
  weights:
    tests_comprehensive: 0.30
    coverage_high: 0.25
    edge_cases_covered: 0.20
    test_quality_high: 0.15
    documentation_clear: 0.10
  min_score: 0.85

llm_temperature: 0.1
llm_model_preference: qwen2.5-coder:7b

compatible_skills:
  - python
  - typescript
  - go
  - coder
  - architect
  - code_reviewer

tags:
  - role
  - testing
  - quality
```

---

## Part 4: Application Service

### File: `src/vivek/application/services/skill_manager.py`

```python
"""Manage skills and orchestrate skill-augmented execution."""

from typing import List, Optional
from vivek.domain.models.skill import Skill, SkillComposition
from vivek.infrastructure.skills.skill_registry import SkillRegistry
from vivek.domain.planning.services.planner_service import PlannerService
from vivek.domain.execution.services.executor_service import ExecutorService


class SkillManager:
    """Manage skill composition and application."""
    
    def __init__(
        self,
        skill_registry: SkillRegistry,
        planner: PlannerService,
        executor: ExecutorService
    ):
        self.registry = skill_registry
        self.planner = planner
        self.executor = executor
    
    def compose_skills(self, skill_ids: List[str]) -> Optional[SkillComposition]:
        """Create a composition from skill IDs."""
        skills = []
        for skill_id in skill_ids:
            skill = self.registry.get_skill(skill_id)
            if not skill:
                raise ValueError(f"Unknown skill: {skill_id}")
            skills.append(skill)
        
        composition = SkillComposition(skills=skills)
        valid, msg = composition.validate()
        
        if not valid:
            raise ValueError(f"Invalid composition: {msg}")
        
        return composition
    
    def apply_skills_to_planning(
        self,
        user_request: str,
        project_context: str,
        composition: SkillComposition
    ) -> str:
        """Augment planning prompt with skill guidance."""
        traits = composition.get_merged_traits()
        
        augmentation = self._build_augmentation_prompt(traits)
        augmented_request = f"{user_request}\n\n{augmentation}"
        
        return augmented_request
    
    def apply_skills_to_execution(
        self,
        work_item,
        composition: SkillComposition
    ) -> str:
        """Augment execution prompt with skill guidance."""
        traits = composition.get_merged_traits()
        augmentation = self._build_execution_augmentation(traits)
        
        return augmentation
    
    def _build_augmentation_prompt(self, traits) -> str:
        """Build augmentation text from traits."""
        prompt = "Apply these considerations:\n"
        for trait in traits:
            prompt += f"- {trait.description}\n"
        return prompt
    
    def _build_execution_augmentation(self, traits) -> str:
        """Build execution-specific augmentation."""
        return self._build_augmentation_prompt(traits)
    
    def get_recommended_composition(
        self,
        language: Optional[str] = None,
        role: Optional[str] = None
    ) -> SkillComposition:
        """Get recommended skill composition."""
        skills = self.registry.discover_recommended_skills(language, role)
        if not skills:
            raise ValueError("No skills found for recommendation")
        return SkillComposition(skills=skills)
```

---

## Part 5: CLI Integration

### File: `src/vivek/presentation/cli/commands/chat_command.py` (Updated)

```python
"""Chat command with skills support."""

import typer
from typing import Optional, List
from pathlib import Path
from vivek.infrastructure.di_container import DIContainer


def chat_with_skills(
    request: str = typer.Argument(..., help="What to implement"),
    skills: Optional[List[str]] = typer.Option(
        None,
        "--skills",
        "-s",
        help="Skills to apply (e.g., python coder test_engineer)"
    ),
    project_root: Path = typer.Option(
        ".",
        "--project",
        "-p",
        help="Project root directory"
    )
):
    """Generate code with optional skill composition.
    
    Examples:
        vivek chat "Create API endpoint"
        vivek chat "Create API endpoint" --skills python architect
        vivek chat "Create API endpoint" -s python coder test_engineer code_reviewer
    """
    try:
        container = DIContainer()
        skill_manager = container.get_skill_manager()
        orchestrator = container.get_orchestrator()
        
        # Get skill composition if specified
        composition = None
        if skills:
            composition = skill_manager.compose_skills(skills)
            print(f"✅ Activated skills: {', '.join(s.name for s in composition.skills)}")
        
        # Apply skills to request if available
        augmented_request = request
        if composition:
            augmented_request = skill_manager.apply_skills_to_planning(
                request,
                "",
                composition
            )
        
        # Execute with orchestrator
        result = orchestrator.execute_request(augmented_request)
        
        print(f"✅ Complete!")
        print(f"Files created: {len(result['files_created'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)
```

---

## Part 6: Testing Strategy

### File: `tests/unit/domain/models/test_skill.py`

```python
"""Tests for Skill domain model."""

import pytest
from vivek.domain.models.skill import Skill, SkillType, Trait, QualityRubric, LanguageSkill


class TestSkill:
    """Test Skill model."""
    
    @pytest.fixture
    def python_skill(self) -> Skill:
        """Create a Python language skill."""
        return Skill(
            id="python",
            name="Python",
            skill_type=SkillType.LANGUAGE,
            description="Python expertise",
            traits=[
                Trait("use_type_hints", "Include type hints", True, "prompt"),
                Trait("follow_pep8", "Follow PEP 8", True, "prompt"),
            ],
            compatible_skills=["coder", "architect"],
            llm_temperature=0.2
        )
    
    @pytest.fixture
    def coder_skill(self) -> Skill:
        """Create a Coder role skill."""
        return Skill(
            id="coder",
            name="Coder",
            skill_type=SkillType.ROLE,
            description="Pragmatic coder",
            traits=[
                Trait("pragmatic", "Get it done", True, "prompt"),
                Trait("simple_code", "Keep it simple", True, "prompt"),
            ]
        )
    
    def test_skill_creation(self, python_skill):
        """Test creating a skill."""
        assert python_skill.id == "python"
        assert python_skill.name == "Python"
        assert python_skill.skill_type == SkillType.LANGUAGE
        assert len(python_skill.traits) == 2
    
    def test_skill_compatibility(self, python_skill, coder_skill):
        """Test skill compatibility checking."""
        assert python_skill.is_compatible_with(coder_skill)
    
    def test_skill_incompatibility(self, python_skill):
        """Test incompatible skills."""
        python_skill.incompatible_skills = ["go"]
        
        go_skill = Skill(
            id="go",
            name="Go",
            skill_type=SkillType.LANGUAGE,
            description="Go expertise"
        )
        
        assert not python_skill.is_compatible_with(go_skill)
    
    def test_merge_traits(self, python_skill, coder_skill):
        """Test merging traits from multiple skills."""
        merged = python_skill.merge_traits_with(coder_skill)
        
        assert len(merged) == 4  # All traits
        trait_names = [t.name for t in merged]
        assert "use_type_hints" in trait_names
        assert "pragmatic" in trait_names
```

### File: `tests/unit/infrastructure/test_skill_loader.py`

```python
"""Tests for skill loading."""

import pytest
from pathlib import Path
from vivek.infrastructure.skills.skill_loader import SkillLoader


class TestSkillLoader:
    """Test skill loading from YAML."""
    
    def test_load_python_skill(self):
        """Test loading Python skill from YAML."""
        loader = SkillLoader()
        
        # Load from actual YAML file
        python_yaml = Path(__file__).parent.parent.parent / \
                      "fixtures" / "skills" / "python.yaml"
        
        skill = loader.load_from_file(python_yaml)
        
        assert skill.id == "python"
        assert skill.name == "Python Language Skill"
        assert len(skill.traits) > 0
        assert skill.quality_rubric is not None
    
    def test_load_from_dict(self):
        """Test loading skill from dictionary."""
        loader = SkillLoader()
        
        data = {
            "id": "test_skill",
            "name": "Test Skill",
            "type": "language",
            "description": "Test",
            "traits": [
                {
                    "name": "test_trait",
                    "description": "Test trait",
                    "value": True,
                    "impact_area": "prompt"
                }
            ]
        }
        
        skill = loader.load_from_dict(data)
        
        assert skill.id == "test_skill"
        assert len(skill.traits) == 1
```

---

## Part 7: Integration Points

### File: `src/vivek/infrastructure/di_container.py` (Updated)

```python
# Add these to DI container:

def get_skill_registry(self) -> SkillRegistry:
    """Get skill registry singleton."""
    if not hasattr(self, '_skill_registry'):
        self._skill_registry = SkillRegistry()
    return self._skill_registry

def get_skill_manager(self) -> SkillManager:
    """Get skill manager."""
    return SkillManager(
        skill_registry=self.get_skill_registry(),
        planner=self.get_planner_service(),
        executor=self.get_executor_service()
    )
```

---

## Detailed Implementation Guide

### 5.1: Skill Prompts - Implementation Details

#### File: `src/vivek/skills/prompts/templates.py`

```python
"""Skill-specific system prompts for LLM guidance."""

class SkillPromptTemplates:
    """Repository of skill-specific prompts."""
    
    CODER_SYSTEM_PROMPT = """You are an expert pragmatic coder focused on clean,
maintainable, working code. Your approach:
- Write code that works first, optimize second
- Keep implementations simple and clear
- Include comprehensive error handling
- Write self-documenting code
- Test as you write"""
    
    ARCHITECT_SYSTEM_PROMPT = """You are a software architect focused on system design
and long-term maintainability. Your approach:
- Design before implementation
- Document key decisions (ADRs)
- Consider scalability from the start
- Balance simplicity with extensibility
- Provide clear implementation guidance"""
    
    TEST_ENGINEER_SYSTEM_PROMPT = """You are a test engineer focused on comprehensive
quality validation. Your approach:
- Write tests first, then implementation
- Aim for >90% code coverage
- Test edge cases exhaustively
- Include performance benchmarks
- Document test strategy"""
    
    PYTHON_LANGUAGE_PROMPT = """Generate Python code following these standards:
- Use type hints for all functions
- Follow PEP 8 style guidelines
- Use modern Python patterns (3.10+)
- Include docstrings for public APIs
- Handle errors explicitly
- Use dataclasses for models"""
    
    @classmethod
    def get_prompt(cls, skill_id: str) -> str:
        """Get system prompt for skill."""
        attr_name = f"{skill_id.upper()}_SYSTEM_PROMPT"
        return getattr(cls, attr_name, "")
```

#### File: `src/vivek/skills/prompts/skill_prompt_injector.py`

```python
"""Inject skill prompts into execution context."""

class SkillPromptInjector:
    """Merge skill prompts into LLM context."""
    
    def inject_into_execution(
        self,
        original_prompt: str,
        skills: List[Skill]
    ) -> str:
        """Inject skill prompts into execution prompt."""
        skill_guidance = self._build_skill_section(skills)
        
        # Insert skill guidance before main request
        return f"{skill_guidance}\n\n{original_prompt}"
    
    def inject_into_planning(
        self,
        original_request: str,
        skills: List[Skill]
    ) -> str:
        """Inject skill prompts into planning phase."""
        guidance = self._build_planning_guidance(skills)
        return f"{guidance}\n\nUser Request:\n{original_request}"
    
    def _build_skill_section(self, skills: List[Skill]) -> str:
        """Build combined skill guidance."""
        sections = []
        for skill in skills:
            prompt = SkillPromptTemplates.get_prompt(skill.id)
            if prompt:
                sections.append(f"[{skill.name}]\n{prompt}")
        
        return "\n\n".join(sections)
```

#### Success Metrics for 5.1
- [ ] All 7 skill prompts defined
- [ ] Prompt injection tests: 20+
- [ ] Quality improvement: 15-25%
- [ ] Response consistency: 85%+

---

### 5.2: Skill Executors - Implementation Details

#### File: `src/vivek/llm/executors/skill_executor.py`

```python
"""Base executor for skill-aware execution."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from vivek.domain.models.skill import Skill, Trait


class SkillExecutor(ABC):
    """Abstract base for skill-specific executors."""
    
    def __init__(self, skills: List[Skill]):
        self.skills = skills
        self.traits = self._merge_traits()
    
    @property
    @abstractmethod
    def skill_type(self) -> str:
        """Type of skill this executor handles."""
        pass
    
    def pre_execution_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before execution begins."""
        return context
    
    def transform_prompt(
        self,
        prompt: str,
        traits: List[Trait]
    ) -> str:
        """Transform prompt based on traits."""
        injector = SkillPromptInjector()
        return injector.inject_into_execution(prompt, self.skills)
    
    def post_execution_hook(
        self,
        result: str,
        context: Dict[str, Any]
    ) -> str:
        """Hook after execution completes."""
        return result
    
    def evaluate_output(self, output: str) -> Dict[str, float]:
        """Evaluate output against skill rubrics."""
        scores = {}
        for skill in self.skills:
            if skill.quality_rubric:
                score = self._evaluate_against_rubric(output, skill)
                scores[skill.id] = score
        return scores
    
    def _merge_traits(self) -> List[Trait]:
        """Merge traits from all skills."""
        all_traits = []
        for skill in self.skills:
            all_traits.extend(skill.traits)
        return all_traits
    
    def _evaluate_against_rubric(self, output: str, skill: Skill) -> float:
        """Score output against skill rubric."""
        # Placeholder - implement with LLM evaluator
        pass
```

#### File: `src/vivek/llm/executors/specialized/coder_executor.py`

```python
class CoderExecutor(SkillExecutor):
    """Executor focused on pragmatic code generation."""
    
    skill_type = "coder"
    
    def transform_prompt(self, prompt: str, traits: List[Trait]) -> str:
        """Add pragmatic coding guidance."""
        coder_guidance = """Write pragmatic, working code:
        1. Focus on correctness first
        2. Keep implementations simple
        3. Handle errors explicitly
        4. Write clear variable names
        5. Include brief comments for complex logic"""
        
        return f"{coder_guidance}\n\n{prompt}"
    
    def post_execution_hook(self, result: str, context: Dict) -> str:
        """Ensure code is executable."""
        # Validate syntax
        # Check for common errors
        # Suggest improvements
        return result
```

#### Success Metrics for 5.2
- [ ] SkillExecutor base class complete
- [ ] 4+ specialized executors working
- [ ] Executor tests: 40+
- [ ] Composition functional: 10+ tests
- [ ] Backward compatibility: 100%

---

### 5.3: Skill Phases - Implementation Details

#### File: `src/vivek/domain/models/skill_phase.py`

```python
"""Skill execution phases."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ExecutionPhase(Enum):
    """Execution phases in work process."""
    PLANNING = "planning"
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"


@dataclass
class SkillPhaseConfig:
    """Configuration for skill in a phase."""
    phase: ExecutionPhase
    skills_active: List[str]
    prompt_prefix: str
    exit_criteria: List[str]  # e.g., ["design_complete", "requirements_clear"]
    timeout_minutes: int = 30
    allow_iteration: bool = True
```

#### File: `src/vivek/core/phase_router.py`

```python
"""Route execution through skill phases."""

class PhaseRouter:
    """Orchestrate multi-phase execution with skills."""
    
    def route_to_phases(
        self,
        request: str,
        skills: List[Skill]
    ) -> Dict[ExecutionPhase, str]:
        """Execute request through all phases."""
        results = {}
        
        # Phase 1: Planning (Architect)
        plan = self._execute_phase(
            ExecutionPhase.PLANNING,
            request,
            ["architect"]
        )
        results[ExecutionPhase.PLANNING] = plan
        
        # Phase 2: Analysis (Test Engineer)
        analysis = self._execute_phase(
            ExecutionPhase.ANALYSIS,
            plan,
            ["test_engineer"]
        )
        results[ExecutionPhase.ANALYSIS] = analysis
        
        # Phase 3: Implementation (Coder + Language)
        implementation = self._execute_phase(
            ExecutionPhase.IMPLEMENTATION,
            analysis,
            ["coder", "python"]  # Language from composition
        )
        results[ExecutionPhase.IMPLEMENTATION] = implementation
        
        # Phase 4: Review (Code Reviewer)
        reviewed = self._execute_phase(
            ExecutionPhase.REVIEW,
            implementation,
            ["code_reviewer"]
        )
        results[ExecutionPhase.REVIEW] = reviewed
        
        return results
```

#### Success Metrics for 5.3
- [ ] Phase model complete
- [ ] All 4 phases working
- [ ] Phase routing tests: 35+
- [ ] Context propagation: 15+ tests
- [ ] Iteration support: functional

---

### 5.4: Workflow DAG - Implementation Details

#### File: `src/vivek/domain/models/workflow_dag.py`

```python
"""Workflow DAG for skill orchestration."""

from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
from enum import Enum


class NodeType(Enum):
    """Types of DAG nodes."""
    SKILL = "skill"
    CONTROL = "control"  # if/then/merge
    DATA = "data"  # input/output


@dataclass
class DAGNode:
    """Node in skill workflow DAG."""
    id: str
    node_type: NodeType
    skill_id: Optional[str] = None  # For skill nodes
    dependencies: List[str] = field(default_factory=list)
    parallel_with: List[str] = field(default_factory=list)


class WorkflowDAG:
    """Directed acyclic graph of skill workflow."""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: List[Tuple[str, str]] = []
    
    def add_skill_node(self, skill_id: str, depends_on: List[str] = None):
        """Add skill execution node."""
        node = DAGNode(
            id=skill_id,
            node_type=NodeType.SKILL,
            skill_id=skill_id,
            dependencies=depends_on or []
        )
        self.nodes[skill_id] = node
    
    def validate(self) -> Tuple[bool, str]:
        """Validate DAG is acyclic."""
        if self._has_cycle():
            return False, "DAG contains cycle"
        return True, "Valid DAG"
    
    def get_execution_order(self) -> List[str]:
        """Topological sort for execution order."""
        # Kahn's algorithm
        pass
    
    def get_parallelizable_nodes(self) -> List[List[str]]:
        """Get groups of nodes that can run in parallel."""
        pass
```

#### File: `src/vivek/core/dag_executor.py`

```python
"""Execute workflows defined as DAGs."""

class DAGExecutor:
    """Execute DAG-based workflows."""
    
    async def execute(self, dag: WorkflowDAG, input_data: Dict) -> Dict:
        """Execute DAG respecting dependencies."""
        execution_order = dag.get_execution_order()
        results = {}
        
        for node_id in execution_order:
            # Check if can parallelize
            parallel_nodes = dag.get_parallelizable_nodes()
            
            if node_id in parallel_nodes:
                # Execute in parallel
                results.update(await self._execute_parallel(parallel_nodes))
            else:
                # Execute sequentially
                results[node_id] = await self._execute_node(node_id, results)
        
        return results
    
    async def _execute_node(self, node_id: str, context: Dict) -> str:
        """Execute single DAG node."""
        pass
```

#### Success Metrics for 5.4
- [ ] DAG model complete with validation
- [ ] Topological sort working
- [ ] Parallel execution: 5+ tests
- [ ] DAG visualizer: Mermaid output
- [ ] Integration tests: 45+

---

### 5.5: Quality Rubrics - Implementation Details

#### File: `src/vivek/domain/services/rubric_evaluator.py`

```python
"""Evaluate output against quality rubrics."""

class RubricEvaluator:
    """Score artifacts against skill rubrics."""
    
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    async def evaluate(
        self,
        artifact: str,
        rubric: QualityRubric
    ) -> Dict[str, Any]:
        """Evaluate artifact against rubric."""
        evaluation_prompt = self._build_eval_prompt(artifact, rubric)
        
        result = await self.llm.call(evaluation_prompt)
        scores = self._parse_scores(result)
        
        return {
            "scores": scores,
            "overall": sum(scores.values()) / len(scores),
            "feedback": result,
            "passes": sum(scores.values()) / len(scores) >= rubric.min_score
        }
    
    def _build_eval_prompt(self, artifact: str, rubric: QualityRubric) -> str:
        """Build LLM evaluation prompt."""
        criteria_text = "\n".join(rubric.criteria)
        return f"""Evaluate this artifact against these criteria:

{criteria_text}

Artifact:
{artifact}

Provide scores 0-100 for each criterion."""
```

#### File: `src/vivek/core/feedback_loop_orchestrator.py`

```python
"""Manage quality feedback loops."""

class FeedbackLoopOrchestrator:
    """Coordinate refinement based on quality gaps."""
    
    async def refine_until_quality(
        self,
        artifact: str,
        rubric: QualityRubric,
        max_iterations: int = 3
    ) -> str:
        """Iteratively improve artifact until quality threshold."""
        current = artifact
        
        for iteration in range(max_iterations):
            eval_result = await self.evaluator.evaluate(current, rubric)
            
            if eval_result["passes"]:
                return current
            
            # Route to appropriate skill for refinement
            refined = await self._refine(current, eval_result["feedback"])
            current = refined
        
        return current
```

#### Success Metrics for 5.5
- [ ] Rubric evaluator functional
- [ ] LLM evaluation prompts effective
- [ ] Feedback loops working: 10+ tests
- [ ] Quality improvements measurable
- [ ] Dashboard functional (optional)

---

## Integration Checklist

### 5.1 Integration Points
- [ ] Connect to PlannerService
- [ ] Connect to ExecutorService  
- [ ] Update CLI with prompt injection
- [ ] Add configuration for prompt templates

### 5.2 Integration Points
- [ ] Register executors in DI container
- [ ] Connect to LangGraph nodes
- [ ] Update execution pipeline
- [ ] Add executor selection logic

### 5.3 Integration Points
- [ ] Add phase nodes to LangGraph
- [ ] Implement phase routing in orchestrator
- [ ] Connect context propagation
- [ ] Add phase CLI options

### 5.4 Integration Points
- [ ] DAG builder from skill composition
- [ ] LangGraph DAG executor mapping
- [ ] Visualization in CLI
- [ ] DAG validation in composition

### 5.5 Integration Points
- [ ] Hook into execution completion
- [ ] Add quality check gate in pipeline
- [ ] Dashboard server endpoints
- [ ] Configuration for feedback loops

---

## Deliverables Checklist

### 5.1: Skill Prompts
- [ ] 7 core skill prompts defined
- [ ] Prompt injection system working
- [ ] 20+ prompt injection tests
- [ ] Quality metrics +15-25%
- [ ] Documentation complete

### 5.2: Skill Executors
- [ ] SkillExecutor base class
- [ ] 4+ specialized executors
- [ ] Executor composition
- [ ] 40+ executor tests
- [ ] Backward compatibility verified

### 5.3: Skill Phases
- [ ] Phase model complete
- [ ] 4 phases implemented
- [ ] Phase router working
- [ ] 35+ phase tests
- [ ] Multi-turn reasoning improved

### 5.4: Workflow DAG
- [ ] DAG model with validation
- [ ] DAG executor functional
- [ ] Parallel execution support
- [ ] 45+ DAG tests
- [ ] Visualization working

### 5.5: Quality Rubrics
- [ ] Rubric evaluator complete
- [ ] Feedback loops functional
- [ ] 40+ rubric tests
- [ ] Quality improvements measurable
- [ ] Optional flag for disable

---

## Overall Success Criteria

✅ All 5 sub-workstreams complete and integrated
✅ 140+ total tests passing (>85% coverage)
✅ Performance overhead < 10%
✅ Backward compatibility 100%
✅ Documentation comprehensive
✅ Quality metrics improving 20-40%
✅ Skills composition working end-to-end

````
