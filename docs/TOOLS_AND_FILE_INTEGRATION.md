# Vivek: Tools & File Integration Guide (CLI Tool)

> ⚠️ **ARCHIVED**: File operations details have been integrated into Workstream 1.
> FileService and CommandExecutor implementations are in the workstreams.
> This document is kept for reference only.

**Document Type**: Technical Reference (REFERENCE ONLY)
**Version**: 2.1
**Last Updated**: October 22, 2025
**Status**: ARCHIVED - See Workstream 1
**Scope**: File editing, command execution for standalone CLI tool

---

## Executive Summary

This document defines the **file operations**, **decision framework**, and **implementation strategy** for Vivek as a **standalone command-line tool**. Vivek directly manipulates files using Python's standard library and open-source tools.

### Key Clarifications
- **Tool Type**: Standalone CLI tool (NOT a VSCode extension)
- **File Operations**: Direct Python file I/O using `pathlib`, `open()`, etc.
- **Decision Framework**: When to use text replacement, AST, or templates
- **Implementation Path**: v4.0.0 (direct), v4.1.0 (enhanced), v4.2.0+ (advanced)

---

## Part 1: Architecture Clarification

### 1.1 Vivek as a Standalone CLI Tool

```
User runs: vivek chat "Create a FastAPI endpoint"
    ↓
Vivek CLI (Python application)
    ↓
┌─────────────────────────────────────┐
│  Vivek Orchestrator                  │
│  (Pure Python Application)           │
│                                      │
│  ├─ LLM Providers                   │
│  │  └─ Ollama, OpenAI, Anthropic   │
│  │                                   │
│  ├─ File Operations (Python)        │
│  │  ├─ pathlib.Path.read_text()    │
│  │  ├─ pathlib.Path.write_text()   │
│  │  └─ open(), read(), write()     │
│  │                                   │
│  ├─ AST Operations (Python libs)    │
│  │  ├─ libcst (Python AST)         │
│  │  └─ tree-sitter (Multi-lang)    │
│  │                                   │
│  ├─ Command Execution               │
│  │  └─ subprocess.run()             │
│  │                                   │
│  └─ Quality Validation              │
│     ├─ ast.parse() for syntax      │
│     └─ subprocess for linting       │
└─────────────────────────────────────┘
    ↓
Files written directly to filesystem
```

### 1.2 File Operation Methods

Vivek uses **standard Python libraries** for file operations:

| Operation | Library/Method | When to Use |
|-----------|----------------|-------------|
| **Read file** | `pathlib.Path.read_text()` | Read entire file |
| **Write file** | `pathlib.Path.write_text()` | Create or overwrite file |
| **Create directory** | `pathlib.Path.mkdir(parents=True)` | Create nested directories |
| **Check exists** | `pathlib.Path.exists()` | Before reading |
| **List files** | `pathlib.Path.glob()`, `rglob()` | Find files by pattern |
| **Run commands** | `subprocess.run()` | Execute tests, linters, builds |

---

## Part 2: File Operations API (Vivek Internal)

### 2.1 Core File Operations

```python
from pathlib import Path
from typing import Optional, List

class FileOperations:
    """Core file operations for Vivek CLI."""

    @staticmethod
    def read_file(file_path: str, start_line: Optional[int] = None,
                  end_line: Optional[int] = None) -> str:
        """Read file content (optionally with line range)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text()

        if start_line or end_line:
            lines = content.split('\n')
            start = (start_line - 1) if start_line else 0
            end = end_line if end_line else len(lines)
            return '\n'.join(lines[start:end])

        return content

    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """Write content to file (creates parent directories if needed)."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return True

    @staticmethod
    def edit_file(file_path: str, old_string: str, new_string: str) -> bool:
        """Replace exact text in file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text()

        if old_string not in content:
            raise ValueError(f"String not found in file: {old_string[:50]}...")

        # Replace first occurrence
        new_content = content.replace(old_string, new_string, 1)
        path.write_text(new_content)
        return True

    @staticmethod
    def create_directory(dir_path: str) -> bool:
        """Create directory (including parent directories)."""
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True

    @staticmethod
    def list_files(directory: str, pattern: str = "**/*.py") -> List[str]:
        """List files matching pattern."""
        path = Path(directory)
        return [str(f) for f in path.glob(pattern)]
```

### 2.2 Command Execution

```python
import subprocess
from typing import Dict

class CommandExecutor:
    """Execute shell commands for Vivek CLI."""

    @staticmethod
    def run_command(command: str, cwd: Optional[str] = None,
                   timeout: int = 60) -> Dict[str, any]:
        """Execute shell command and return result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "exit_code": -1
            }

    @staticmethod
    def run_tests(test_path: str, coverage: bool = False) -> Dict[str, any]:
        """Run pytest tests."""
        cmd = f"pytest {test_path} -v"
        if coverage:
            cmd += " --cov --cov-report=term-missing"

        return CommandExecutor.run_command(cmd)

    @staticmethod
    def run_linter(file_path: str, tool: str = "flake8") -> Dict[str, any]:
        """Run linter on file."""
        return CommandExecutor.run_command(f"{tool} {file_path}")

    @staticmethod
    def format_code(file_path: str, tool: str = "black") -> Dict[str, any]:
        """Format code file."""
        return CommandExecutor.run_command(f"{tool} {file_path}")
```

---

## Part 3: Decision Framework for File Operations

### 3.1 Decision Matrix

| Scenario | Approach | Tool/Library | When to Use | Example |
|----------|----------|--------------|-------------|---------|
| **Simple text change** | Direct text replacement | `str.replace()` | Changing config value, fixing typo | Change `timeout: 30` to `timeout: 60` in YAML |
| **Add method to class** | AST transformation | `libcst` (Python) | Preserve formatting, add to specific location | Add `def new_method(self): pass` to existing class |
| **Multi-language refactor** | Universal AST | `tree-sitter` | Language-agnostic parsing | Rename class across Python, TS, Go files |
| **Create new file** | Template generation | `Jinja2` + `write_file()` | Boilerplate code | Generate FastAPI endpoint file with tests |
| **Complex refactoring** | Hybrid | `tree-sitter` + `libcst` | Multi-step transformation | Extract interface, update implementations |
| **Emergency fix** | Direct text replacement | `str.replace()` | Fast, predictable, low risk | Fix syntax error in config |

### 3.2 Decision Tree

```
User Request: "Modify code"
    │
    ├─ Is it a simple text change? (≤5 lines, no logic)
    │   └─ YES → Use Path.read_text() + str.replace() + Path.write_text()
    │
    ├─ Creating new file from template?
    │   └─ YES → Use Jinja2 template + Path.write_text()
    │
    ├─ Need to preserve exact formatting?
    │   └─ YES → Use libcst (Python) or tree-sitter (other languages)
    │
    ├─ Multi-language refactoring?
    │   └─ YES → Use tree-sitter for all languages
    │
    └─ Complex transformation with validation?
        └─ YES → Use libcst + validation + write_file()
```

---

## Part 4: Implementation Examples

### 4.1 Simple Text Replacement

**Scenario**: Update timeout configuration

```python
from pathlib import Path

def update_timeout(config_path: str, old_value: int, new_value: int):
    """Update timeout in config file."""
    path = Path(config_path)
    content = path.read_text()

    old_string = f"timeout: {old_value}"
    new_string = f"timeout: {new_value}"

    if old_string not in content:
        raise ValueError(f"Timeout {old_value} not found in config")

    new_content = content.replace(old_string, new_string)
    path.write_text(new_content)

    print(f"✅ Updated timeout from {old_value} to {new_value}")
```

**Usage**:
```python
update_timeout(".vivek/config.yml", 30, 60)
```

---

### 4.2 AST Transformation (Python)

**Scenario**: Add method to existing class

```python
import libcst as cst
from pathlib import Path

class AddMethodTransformer(cst.CSTTransformer):
    """Add method to a class."""

    def __init__(self, class_name: str, method_code: str):
        self.class_name = class_name
        self.method_node = cst.parse_statement(method_code)

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            # Add method to class body
            return updated_node.with_changes(
                body=updated_node.body.with_changes(
                    body=[*updated_node.body.body, self.method_node]
                )
            )
        return updated_node

def add_method_to_class(file_path: str, class_name: str, method_code: str):
    """Add method to existing Python class."""
    path = Path(file_path)

    # Read file
    code = path.read_text()

    # Parse AST
    module = cst.parse_module(code)

    # Transform
    transformer = AddMethodTransformer(class_name, method_code)
    modified_module = module.visit(transformer)

    # Write back
    path.write_text(modified_module.code)

    print(f"✅ Added method to {class_name} in {file_path}")
```

**Usage**:
```python
method = """
    def calculate_total(self) -> float:
        \"\"\"Calculate invoice total with tax.\"\"\"
        return self.subtotal * (1 + self.tax_rate)
"""

add_method_to_class("src/models/invoice.py", "Invoice", method)
```

---

### 4.3 Template-Based Generation

**Scenario**: Create new FastAPI endpoint from template

```python
from jinja2 import Template
from pathlib import Path

def create_fastapi_endpoint(
    file_path: str,
    prefix: str,
    tag: str,
    model_name: str
):
    """Generate FastAPI endpoint from template."""

    template = Template("""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/{{ prefix }}", tags=["{{ tag }}"])

class {{ model_name }}(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: {{ model_name }}):
    \"\"\"Register a new user.\"\"\"
    # TODO: Hash password
    # TODO: Store in database
    return {"message": "User registered", "email": user.email}
""")

    code = template.render(
        prefix=prefix,
        tag=tag,
        model_name=model_name
    )

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code)

    print(f"✅ Created endpoint at {file_path}")
```

**Usage**:
```python
create_fastapi_endpoint(
    "src/routes/auth.py",
    prefix="/auth",
    tag="authentication",
    model_name="UserRegistration"
)
```

---

### 4.4 Running Tests and Validation

```python
import subprocess
from pathlib import Path

def validate_and_test(file_path: str):
    """Validate syntax and run tests for a file."""
    path = Path(file_path)

    # 1. Check syntax
    print("🔍 Checking syntax...")
    try:
        code = path.read_text()
        compile(code, file_path, 'exec')
        print("✅ Syntax valid")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

    # 2. Run linter
    print("🔍 Running linter...")
    result = subprocess.run(
        f"flake8 {file_path}",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Linting passed")
    else:
        print(f"⚠️ Linting warnings:\n{result.stdout}")

    # 3. Run tests (if test file exists)
    test_path = path.parent.parent / "tests" / f"test_{path.name}"
    if test_path.exists():
        print("🔍 Running tests...")
        result = subprocess.run(
            f"pytest {test_path} -v",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Tests passed")
        else:
            print(f"❌ Tests failed:\n{result.stdout}")
            return False

    return True
```

---

## Part 5: Implementation Strategy (Gradual Build)

### 5.1 Version Roadmap

```
v4.0.0 (8 weeks) - Foundation
├─ Direct file I/O (pathlib)
├─ Text replacement (str.replace)
├─ Basic validation (ast.parse)
└─ Command execution (subprocess)

v4.1.0 (4 weeks) - Enhanced
├─ AST transformation (libcst for Python)
├─ Template generation (Jinja2)
├─ Advanced validation (mypy, black)
└─ Semantic file search (embeddings)

v4.2.0+ (4 weeks) - Advanced
├─ Multi-language AST (tree-sitter)
├─ Complex refactoring workflows
├─ LLM function calling for tool selection
└─ Interactive refinement
```

### 5.2 v4.0.0 Implementation (Direct Integration)

**Focus**: Simple, reliable, fast using Python standard library

```python
from pathlib import Path
from typing import Dict, Any

class ExecutorService:
    """Executor for v4.0.0 - Direct file operations."""

    async def execute_work_item(self, item: WorkItem) -> ExecutionResult:
        """Execute work item using direct file I/O."""

        # 1. Generate code (LLM)
        prompt = self.build_prompt(item)
        code = await self.llm.generate(prompt)

        # 2. Validate syntax (direct)
        errors = self.validate_syntax(code, item.language)
        if errors:
            return ExecutionResult(success=False, errors=errors)

        # 3. Write file (pathlib)
        file_path = Path(item.file_path)

        if item.file_status == "new":
            # Create new file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code)
        else:
            # Update existing file (replace entire content)
            existing = file_path.read_text()
            file_path.write_text(code)

        return ExecutionResult(success=True, code=code)

    def validate_syntax(self, code: str, language: str) -> List[str]:
        """Validate code syntax."""
        errors = []

        if language == "python":
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                errors.append(f"Line {e.lineno}: {e.msg}")

        return errors
```

**Characteristics**:
- ✅ Simple: Direct Python file I/O
- ✅ Fast: No external dependencies
- ✅ Reliable: Standard library only
- ✅ Cross-platform: Works on Windows, Linux, Mac

---

### 5.3 v4.1.0 Implementation (AST Enhancement)

```python
import libcst as cst
from pathlib import Path

class ExecutorServiceV2:
    """Executor for v4.1.0 - AST enhancement."""

    def __init__(self):
        self.use_ast = True  # Enable AST transformations

    async def execute_work_item(self, item: WorkItem) -> ExecutionResult:
        """Execute with AST transformation when applicable."""

        # Decide: AST or direct?
        if self.should_use_ast(item):
            return await self.execute_with_ast(item)
        else:
            return await self.execute_direct(item)

    def should_use_ast(self, item: WorkItem) -> bool:
        """Decide if AST transformation is needed."""
        return (
            item.transformation_type in ["add_method", "refactor_class"] or
            item.preserve_formatting is True or
            item.complexity > 3
        )

    async def execute_with_ast(self, item: WorkItem) -> ExecutionResult:
        """Execute using AST transformation."""
        file_path = Path(item.file_path)

        # 1. Read existing code
        existing_code = file_path.read_text()

        # 2. Parse AST
        if item.language == "python":
            module = cst.parse_module(existing_code)

            # 3. Transform
            transformer = self.get_transformer(item)
            modified_module = module.visit(transformer)
            new_code = modified_module.code
        else:
            # Fallback to direct for non-Python
            new_code = existing_code

        # 4. Validate
        errors = self.validate_syntax(new_code, item.language)
        if errors:
            return ExecutionResult(success=False, errors=errors)

        # 5. Write back
        file_path.write_text(new_code)

        return ExecutionResult(success=True, code=new_code)
```

---

## Part 6: Context Window Management

### 6.1 Token Budget Allocation

```python
from pathlib import Path
from typing import List, Dict

class ContextWindowManager:
    """Manage context window for LLM prompts."""

    def __init__(self, model_max_tokens: int = 8192):
        self.model_max_tokens = model_max_tokens
        self.system_prompt_tokens = 500
        self.user_instruction_tokens = 200
        self.output_buffer_tokens = 2000
        self.available_for_context = (
            model_max_tokens
            - self.system_prompt_tokens
            - self.user_instruction_tokens
            - self.output_buffer_tokens
        )  # = 5492 tokens

    def build_context(self, work_item: WorkItem, project_root: str) -> str:
        """Build context respecting token limits."""

        allocation = {
            "current_file": int(self.available_for_context * 0.40),  # 2197
            "dependencies": int(self.available_for_context * 0.30),  # 1648
            "similar_files": int(self.available_for_context * 0.15), # 824
            "type_defs": int(self.available_for_context * 0.10),     # 549
            "conventions": int(self.available_for_context * 0.05)    # 274
        }

        context_parts = []

        # 1. Current file (highest priority)
        if work_item.file_status == "existing":
            file_path = Path(work_item.file_path)
            if file_path.exists():
                current = file_path.read_text()
                current = self.truncate_text(current, allocation["current_file"])
                context_parts.append(f"# Current File:\n{current}")

        # 2. Dependencies
        deps = self.get_dependencies(work_item.file_path, project_root)
        for dep in deps[:3]:  # Limit to top 3
            dep_path = Path(dep)
            if dep_path.exists():
                dep_content = dep_path.read_text()
                dep_content = self.truncate_text(
                    dep_content,
                    allocation["dependencies"] // 3
                )
                context_parts.append(f"# Dependency: {dep}\n{dep_content}")

        # 3. Project conventions
        conventions = self.get_conventions(project_root)
        conv_content = self.truncate_text(
            conventions,
            allocation["conventions"]
        )
        context_parts.append(f"# Conventions:\n{conv_content}")

        return "\n\n".join(context_parts)

    def get_dependencies(self, file_path: str, project_root: str) -> List[str]:
        """Extract import dependencies from file."""
        path = Path(file_path)
        if not path.exists():
            return []

        content = path.read_text()
        dependencies = []

        # Parse imports (simple regex-based for now)
        import re
        for line in content.split('\n'):
            if line.startswith('import ') or line.startswith('from '):
                match = re.search(r'from ([\w.]+)', line) or re.search(r'import ([\w.]+)', line)
                if match:
                    module = match.group(1)
                    # Convert to file path
                    dep_path = Path(project_root) / "src" / module.replace('.', '/') / "__init__.py"
                    if dep_path.exists():
                        dependencies.append(str(dep_path))

        return dependencies

    def truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token budget."""
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n... (truncated)"
```

---

## Part 7: Cost-Benefit Analysis

### 7.1 Latency Comparison

| Approach | Avg Latency | Dependencies | Reliability |
|----------|-------------|--------------|-------------|
| **Direct (v4.0.0)** | ~2-3s | stdlib only | 95%+ |
| **AST (v4.1.0)** | ~3-5s | + libcst | 98%+ |
| **Function Calling (v4.2.0+)** | ~5-10s | + various | 85-90% |

### 7.2 When to Use Each Approach

| Criteria | Direct (stdlib) | AST (libcst) | Template (Jinja2) |
|----------|-----------------|--------------|-------------------|
| **Speed matters** | ✅ Use | ⚠️ OK | ✅ Use |
| **Format preservation** | ❌ No | ✅ Use | ⚠️ Depends |
| **New file creation** | ✅ Use | ❌ Overkill | ✅ Use |
| **Modify existing** | ⚠️ OK | ✅ Use | ❌ No |
| **Simple change** | ✅ Use | ❌ Overkill | ❌ Overkill |

---

## Part 8: Summary

### Tool Decision Summary

| Task | v4.0.0 | v4.1.0 | v4.2.0+ |
|------|--------|--------|---------|
| Simple text change | `Path.read_text()` + `str.replace()` | Same | Same |
| Add method to class | Full file rewrite | `libcst` | `libcst` + function calling |
| Create new file | `Path.write_text()` | `Jinja2` + `Path.write_text()` | Same |
| Multi-language refactor | Not supported | `tree-sitter` | `tree-sitter` + function calling |
| Run tests | `subprocess.run("pytest")` | Same with parsing | Same with validation |

### Implementation Path

```
v4.0.0 (8 weeks)
├─ pathlib for file I/O
├─ str.replace for editing
├─ subprocess for commands
└─ ast.parse for validation

v4.1.0 (4 weeks)
├─ libcst for Python AST
├─ Jinja2 for templates
├─ Advanced validation
└─ Semantic file search

v4.2.0+ (4 weeks)
├─ tree-sitter for multi-lang
├─ LLM function calling
├─ Complex refactoring
└─ Interactive refinement
```

### Key Takeaways

1. **Standalone CLI**: Vivek is a pure Python CLI tool, not a VSCode extension
2. **Standard Library First**: v4.0.0 uses `pathlib`, `subprocess`, `ast` - no external file APIs
3. **Gradual Enhancement**: Add `libcst`, `Jinja2`, `tree-sitter` in later versions
4. **Cross-Platform**: Works on Windows, Linux, macOS out of the box
5. **Simple to Complex**: Start with direct file I/O, evolve to AST transformations

---

**Document Status**: Complete (Corrected for CLI Tool)
**Version**: 2.1
**Last Updated**: October 22, 2025
