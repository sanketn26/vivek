# Workstream 5: Skills System

**Timeline**: Week 7-12 (6 weeks)
**Goal**: Add specialized domain expertise via Skills composition

**Prerequisites**: Workstreams 1-4 complete

---

## Overview

This workstream implements the Skills System - transforming Vivek from a general-purpose assistant into a specialized multi-disciplinary professional platform with composable expertise.

### Deliverables
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

## Deliverables Checklist

- [ ] Phase 1: Domain models complete (40 tests)
- [ ] Phase 2: Infrastructure complete (30 tests)  
- [ ] Phase 3: All 7 skills defined in YAML
- [ ] Phase 4: CLI integration complete (20 tests)
- [ ] Phase 5: Integration tests pass (50 tests)
- [ ] Phase 6: Documentation complete
- [ ] Total: 90+ tests, >85% coverage

---

## Success Criteria

✅ All 7 skills implemented and loadable
✅ Skill composition works correctly
✅ CLI supports --skills flag
✅ Quality rubrics integrated
✅ Custom skills extensible
✅ 90+ unit tests passing
✅ >85% code coverage
