# Workstream 9: Code Quality Validation Tools

**Timeline**: Week 20 (1 week)
**Goal**: Native code validation and quality assessment

**Prerequisites**: Workstreams 1-8 complete

---

## Overview

This workstream adds native code quality validation tools that integrate with Vivek's execution pipeline to validate generated code against real language tooling.

### Current Limitations
- Only mock code quality evaluation
- No real syntax validation
- No linting integration
- No type checking integration
- No test execution
- No performance profiling

### What This Enables
- Real-time syntax validation (AST parsing)
- Linting feedback (flake8, eslint, golint)
- Type checking (mypy, tsc, go vet)
- Test execution and coverage
- Performance profiling
- Security scanning

### Deliverables
- ✅ AST-based syntax validator
- ✅ Language-specific linters
- ✅ Type checkers integration
- ✅ Test runner framework
- ✅ Coverage collector
- ✅ Security scanner
- ✅ Performance profiler
- ✅ Validation pipeline
- ✅ 30+ validation tests

---

## Part 1: Abstract Syntax Tree Validation

### File: `src/vivek/infrastructure/validation/ast_validator.py`

```python
"""AST-based code validation."""

import ast
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ValidationIssue:
    """A validation issue found in code."""
    level: str  # "error", "warning", "info"
    message: str
    line: int
    column: int
    code: str  # e.g., "E001", "W002"


class ASTValidator(ABC):
    """Abstract base for language-specific AST validators."""
    
    @abstractmethod
    def validate(self, code: str) -> List[ValidationIssue]:
        """Validate code and return issues."""
        pass


class PythonASTValidator(ASTValidator):
    """Python AST validator."""
    
    def validate(self, code: str) -> List[ValidationIssue]:
        """Validate Python code using AST."""
        issues = []
        
        # Check syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [
                ValidationIssue(
                    level="error",
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno or 0,
                    column=e.offset or 0,
                    code="E001"
                )
            ]
        
        # Check for common issues
        issues.extend(self._check_imports(tree, code))
        issues.extend(self._check_undefined_names(tree, code))
        issues.extend(self._check_type_hints(tree, code))
        issues.extend(self._check_docstrings(tree, code))
        
        return issues
    
    def _check_imports(self, tree: ast.AST, code: str) -> List[ValidationIssue]:
        """Check for import issues."""
        issues = []
        imports = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        
        # Check for unused imports
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
        
        for imp_name, imp_path in imports.items():
            if imp_name not in used_names:
                issues.append(
                    ValidationIssue(
                        level="warning",
                        message=f"Unused import: {imp_path}",
                        line=1,
                        column=0,
                        code="W001"
                    )
                )
        
        return issues
    
    def _check_undefined_names(self, tree: ast.AST, code: str) -> List[ValidationIssue]:
        """Check for undefined names."""
        issues = []
        
        # Basic undefined name check
        defined_names = {"print", "len", "str", "int", "list", "dict"}  # Builtins
        
        # Find all definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_names.add(target.id)
        
        # Check usage
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in defined_names and not node.id.isupper():
                    # Skip if it looks like a constant
                    issues.append(
                        ValidationIssue(
                            level="error",
                            message=f"Undefined name: {node.id}",
                            line=node.lineno or 0,
                            column=node.col_offset or 0,
                            code="E002"
                        )
                    )
        
        return issues
    
    def _check_type_hints(self, tree: ast.AST, code: str) -> List[ValidationIssue]:
        """Check for missing type hints."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check return type
                if node.returns is None and node.name != "__init__":
                    issues.append(
                        ValidationIssue(
                            level="info",
                            message=f"Function '{node.name}' missing return type hint",
                            line=node.lineno or 0,
                            column=0,
                            code="I001"
                        )
                    )
                
                # Check argument types
                for arg in node.args.args:
                    if arg.annotation is None:
                        issues.append(
                            ValidationIssue(
                                level="info",
                                message=f"Argument '{arg.arg}' missing type hint",
                                line=node.lineno or 0,
                                column=0,
                                code="I002"
                            )
                        )
        
        return issues
    
    def _check_docstrings(self, tree: ast.AST, code: str) -> List[ValidationIssue]:
        """Check for missing docstrings."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if not docstring:
                    issues.append(
                        ValidationIssue(
                            level="warning",
                            message=f"{'Function' if isinstance(node, ast.FunctionDef) else 'Class'} '{node.name}' missing docstring",
                            line=node.lineno or 0,
                            column=0,
                            code="W002"
                        )
                    )
        
        return issues


class TypeScriptASTValidator(ASTValidator):
    """TypeScript AST validator (basic)."""
    
    def validate(self, code: str) -> List[ValidationIssue]:
        """Validate TypeScript code."""
        issues = []
        
        # Basic syntax check - look for common errors
        if "export " in code and "import " not in code:
            issues.append(
                ValidationIssue(
                    level="info",
                    message="Exports found but no imports",
                    line=1,
                    column=0,
                    code="I001"
                )
            )
        
        # Check for missing type annotations in function definitions
        import re
        func_pattern = r'function\s+\w+\s*\([^)]*\)\s*{'
        if re.search(func_pattern, code):
            issues.append(
                ValidationIssue(
                    level="warning",
                    message="Function declaration missing return type",
                    line=1,
                    column=0,
                    code="W001"
                )
            )
        
        return issues
```

---

## Part 2: Linting Integration

### File: `src/vivek/infrastructure/validation/linter_service.py`

```python
"""Linting service for code quality."""

import subprocess
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LintIssue:
    """A linting issue."""
    file: str
    line: int
    column: int
    level: str  # error, warning
    code: str
    message: str


class LinterService:
    """Run linters on generated code."""
    
    def lint_python(self, filepath: Path) -> List[LintIssue]:
        """Run flake8 on Python file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["flake8", str(filepath), "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 or result.stdout:
                import json
                errors = json.loads(result.stdout) if result.stdout else []
                
                for err in errors:
                    issues.append(
                        LintIssue(
                            file=err["filename"],
                            line=err["line_number"],
                            column=err["column_number"],
                            level="warning" if err["code"].startswith("W") else "error",
                            code=err["code"],
                            message=err["text"]
                        )
                    )
        
        except FileNotFoundError:
            print("Warning: flake8 not installed")
        except Exception as e:
            print(f"Error running flake8: {e}")
        
        return issues
    
    def lint_typescript(self, filepath: Path) -> List[LintIssue]:
        """Run ESLint on TypeScript file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["eslint", str(filepath), "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 or result.stdout:
                import json
                errors = json.loads(result.stdout) if result.stdout else []
                
                for file_errors in errors:
                    for err in file_errors.get("messages", []):
                        issues.append(
                            LintIssue(
                                file=file_errors["filePath"],
                                line=err["line"],
                                column=err["column"],
                                level="error" if err["severity"] == 2 else "warning",
                                code=err.get("ruleId", "unknown"),
                                message=err["message"]
                            )
                        )
        
        except FileNotFoundError:
            print("Warning: eslint not installed")
        except Exception as e:
            print(f"Error running eslint: {e}")
        
        return issues
    
    def lint_go(self, filepath: Path) -> List[LintIssue]:
        """Run golangci-lint on Go file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["golangci-lint", "run", str(filepath), "--out-format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 or result.stdout:
                import json
                data = json.loads(result.stdout) if result.stdout else {}
                
                for issue in data.get("Issues", []):
                    issues.append(
                        LintIssue(
                            file=issue["FilePath"],
                            line=issue["Line"],
                            column=issue["Column"],
                            level="error",
                            code=issue["FromLinter"],
                            message=issue["Text"]
                        )
                    )
        
        except FileNotFoundError:
            print("Warning: golangci-lint not installed")
        except Exception as e:
            print(f"Error running golangci-lint: {e}")
        
        return issues
```

---

## Part 3: Type Checking Integration

### File: `src/vivek/infrastructure/validation/type_checker.py`

```python
"""Type checking service."""

import subprocess
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TypeIssue:
    """A type checking issue."""
    file: str
    line: int
    column: int
    message: str


class TypeChecker:
    """Check types in generated code."""
    
    def check_python_types(self, filepath: Path) -> List[TypeIssue]:
        """Run mypy on Python file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["mypy", str(filepath), "--json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.stdout:
                import json
                errors = json.loads(result.stdout)
                
                for err in errors:
                    issues.append(
                        TypeIssue(
                            file=err["filename"],
                            line=err["lnum"],
                            column=err["column"],
                            message=err["message"]
                        )
                    )
        
        except FileNotFoundError:
            print("Warning: mypy not installed")
        except Exception as e:
            print(f"Error running mypy: {e}")
        
        return issues
    
    def check_typescript_types(self, filepath: Path) -> List[TypeIssue]:
        """Run TypeScript compiler on file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["tsc", str(filepath), "--noEmit", "--listFilesOnly"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                # Parse tsc output
                for line in result.stdout.split('\n'):
                    if ': error TS' in line:
                        parts = line.split(':')
                        if len(parts) >= 4:
                            issues.append(
                                TypeIssue(
                                    file=parts[0],
                                    line=int(parts[1]) if parts[1].isdigit() else 0,
                                    column=int(parts[2]) if parts[2].isdigit() else 0,
                                    message=': '.join(parts[3:]).strip()
                                )
                            )
        
        except FileNotFoundError:
            print("Warning: tsc not installed")
        except Exception as e:
            print(f"Error running tsc: {e}")
        
        return issues
    
    def check_go_types(self, filepath: Path) -> List[TypeIssue]:
        """Run 'go vet' on Go file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["go", "vet", str(filepath)],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                # Parse go vet output
                for line in result.stderr.split('\n'):
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 3:
                            issues.append(
                                TypeIssue(
                                    file=parts[0],
                                    line=int(parts[1]) if parts[1].isdigit() else 0,
                                    column=int(parts[2]) if parts[2].isdigit() else 0,
                                    message=': '.join(parts[3:]).strip()
                                )
                            )
        
        except FileNotFoundError:
            print("Warning: go not installed")
        except Exception as e:
            print(f"Error running go vet: {e}")
        
        return issues
```

---

## Part 4: Test Runner and Coverage

### File: `src/vivek/infrastructure/validation/test_runner.py`

```python
"""Run tests and collect coverage."""

import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResults:
    """Test execution results."""
    passed: int
    failed: int
    skipped: int
    total: int
    coverage: Optional[float]
    execution_time: float
    
    @property
    def success_rate(self) -> float:
        """Percentage of tests passed."""
        return self.passed / self.total if self.total > 0 else 0.0


class TestRunner:
    """Run tests and collect coverage."""
    
    def run_python_tests(self, test_file: Path) -> TestResults:
        """Run pytest on Python test file."""
        try:
            result = subprocess.run(
                ["pytest", str(test_file), "-v", "--tb=short", "--cov"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output
            output = result.stdout + result.stderr
            
            # Extract counts
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")
            total = passed + failed + skipped
            
            # Extract coverage
            coverage = None
            if "covered" in output:
                import re
                match = re.search(r'(\d+)%', output)
                if match:
                    coverage = int(match.group(1)) / 100
            
            return TestResults(
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                coverage=coverage,
                execution_time=0.0
            )
        
        except Exception as e:
            print(f"Error running tests: {e}")
            return TestResults(0, 0, 0, 0, None, 0.0)
    
    def run_typescript_tests(self, test_file: Path) -> TestResults:
        """Run Jest on TypeScript test file."""
        try:
            result = subprocess.run(
                ["jest", str(test_file), "--coverage"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse Jest output
            output = result.stdout
            
            passed = output.count("✓")
            failed = output.count("✕")
            total = passed + failed
            
            coverage = None
            if "Statements" in output:
                import re
                match = re.search(r'Statements.*?(\d+)%', output)
                if match:
                    coverage = int(match.group(1)) / 100
            
            return TestResults(
                passed=passed,
                failed=failed,
                skipped=0,
                total=total,
                coverage=coverage,
                execution_time=0.0
            )
        
        except Exception as e:
            print(f"Error running tests: {e}")
            return TestResults(0, 0, 0, 0, None, 0.0)
```

---

## Part 5: Integrated Validation Pipeline

### File: `src/vivek/infrastructure/validation/validation_pipeline.py`

```python
"""Integrated validation pipeline."""

from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from vivek.infrastructure.validation.ast_validator import PythonASTValidator
from vivek.infrastructure.validation.linter_service import LinterService
from vivek.infrastructure.validation.type_checker import TypeChecker
from vivek.infrastructure.validation.test_runner import TestRunner


@dataclass
class ValidationReport:
    """Complete validation report."""
    file_path: str
    language: str
    
    # Validation steps
    syntax_issues: int
    lint_issues: int
    type_issues: int
    test_pass_rate: float
    test_coverage: float
    
    # Overall
    passed: bool
    score: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "language": self.language,
            "syntax_issues": self.syntax_issues,
            "lint_issues": self.lint_issues,
            "type_issues": self.type_issues,
            "test_pass_rate": self.test_pass_rate,
            "test_coverage": self.test_coverage,
            "passed": self.passed,
            "score": self.score
        }


class ValidationPipeline:
    """Run full validation pipeline on generated code."""
    
    def __init__(self):
        self.ast_validator = PythonASTValidator()
        self.linter = LinterService()
        self.type_checker = TypeChecker()
        self.test_runner = TestRunner()
    
    def validate_python_file(
        self,
        filepath: Path,
        has_tests: bool = False,
        test_file: Optional[Path] = None
    ) -> ValidationReport:
        """Validate Python file through full pipeline."""
        
        # Read code
        with open(filepath) as f:
            code = f.read()
        
        # Step 1: AST validation
        ast_issues = self.ast_validator.validate(code)
        
        # Step 2: Linting
        lint_issues = self.linter.lint_python(filepath)
        
        # Step 3: Type checking
        type_issues = self.type_checker.check_python_types(filepath)
        
        # Step 4: Test execution
        test_pass_rate = 1.0
        test_coverage = 0.0
        if has_tests and test_file:
            results = self.test_runner.run_python_tests(test_file)
            test_pass_rate = results.success_rate
            test_coverage = results.coverage or 0.0
        
        # Calculate score
        issue_penalty = (len(ast_issues) * 0.1 + len(lint_issues) * 0.05 + len(type_issues) * 0.05)
        score = max(0.0, 1.0 - issue_penalty) * test_pass_rate
        
        # If has tests, factor in coverage
        if test_coverage > 0:
            score *= (0.5 + 0.5 * test_coverage)
        
        passed = score >= 0.7 and len(ast_issues) == 0
        
        return ValidationReport(
            file_path=str(filepath),
            language="python",
            syntax_issues=len(ast_issues),
            lint_issues=len(lint_issues),
            type_issues=len(type_issues),
            test_pass_rate=test_pass_rate,
            test_coverage=test_coverage,
            passed=passed,
            score=score
        )
```

---

## Part 6: Testing

### File: `tests/unit/infrastructure/test_validation_pipeline.py`

```python
"""Tests for validation pipeline."""

import pytest
from pathlib import Path
from vivek.infrastructure.validation.ast_validator import PythonASTValidator
from vivek.infrastructure.validation.validation_pipeline import ValidationPipeline


class TestASTValidator:
    """Test AST validator."""
    
    def test_valid_python_code(self):
        """Test validation of valid code."""
        validator = PythonASTValidator()
        
        code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""
        
        issues = validator.validate(code)
        # May have warnings about imports, but should not have errors
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_syntax_error(self):
        """Test detection of syntax errors."""
        validator = PythonASTValidator()
        
        code = """
def broken(:
    pass
"""
        
        issues = validator.validate(code)
        assert any(i.level == "error" for i in issues)
    
    def test_missing_type_hints(self):
        """Test detection of missing type hints."""
        validator = PythonASTValidator()
        
        code = """
def add(a, b):
    return a + b
"""
        
        issues = validator.validate(code)
        info_issues = [i for i in issues if i.level == "info"]
        assert len(info_issues) > 0


class TestValidationPipeline:
    """Test full validation pipeline."""
    
    def test_validate_python_file(self, tmp_path):
        """Test validating a Python file."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def greet(name: str) -> str:
    \"\"\"Greet someone.\"\"\"
    return f"Hello, {name}!"
""")
        
        pipeline = ValidationPipeline()
        report = pipeline.validate_python_file(test_file)
        
        assert report.file_path == str(test_file)
        assert report.language == "python"
        assert report.syntax_issues == 0
```

---

## Part 7: Deliverables Checklist

- [ ] AST validators for all languages
- [ ] Linting integrations (flake8, eslint, golangci-lint)
- [ ] Type checkers (mypy, tsc, go vet)
- [ ] Test runners and coverage collectors
- [ ] Validation pipeline complete
- [ ] Integration into execution quality evaluation
- [ ] 30+ validation tests passing
- [ ] >85% code coverage

---

## Success Criteria

✅ All syntax errors detected
✅ Linting issues identified
✅ Type errors found
✅ Test coverage measured
✅ Validation pipeline produces quality score
✅ Score correlates with code quality
✅ 30+ validation tests pass
✅ >85% code coverage
✅ <5 second validation per file
