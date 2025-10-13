# Work Item Breakdown Architecture

## Overview

The Vivek system now uses a **work item breakdown** approach for executing tasks with small LLMs. This provides better control, clearer execution flow, and incremental validation.

## Key Changes

### 1. From Steps to Work Items

**Old Approach (Steps):**
```json
{
  "description": "Create unit tests",
  "mode": "sdet",
  "steps": [
    "Analyze code structure",
    "Write test files",
    "Run tests"
  ],
  "relevant_files": ["test.py"],
  "priority": "normal"
}
```

**New Approach (Work Items):**
```json
{
  "description": "Create unit tests",
  "mode": "sdet",
  "work_items": [
    {
      "mode": "sdet",
      "file_path": "tests/test_module.py",
      "file_status": "new",
      "description": "Create unit tests for module.py covering happy path, edge cases, and error conditions using pytest",
      "dependencies": []
    }
  ],
  "priority": "normal"
}
```

### 2. Work Item Structure

Each work item contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mode` | string | Execution mode | `"coder"`, `"sdet"`, `"architect"`, `"peer"` |
| `file_path` | string | Exact file path | `"src/utils/helper.py"`, `"console"`, `"docs/design.md"` |
| `file_status` | string | File operation | `"new"` (create) or `"existing"` (modify) |
| `description` | string | Detailed instructions | `"Implement X function with Y error handling"` |
| `dependencies` | array | Prerequisite items | `[0, 1]` (indices of other work items) |

### 3. Three-Phase Execution Process

The executor now follows a structured three-phase approach:

#### **PHASE 1: Work Item Breakdown**
For each work item:
1. **ANALYZE**: Understand the specific requirement
2. **SUB-TASKS**: Break into 3-5 atomic sub-tasks
   - Each must be specific, testable, independent
   - Must be in dependency order
3. **VALIDATE**: Check if breakdown covers all requirements

#### **PHASE 2: Incremental Implementation**
For each sub-task:
1. **IMPLEMENT**: Execute following mode guidelines
2. **VERIFY**: Check output meets requirements
3. **CHECKPOINT**: Confirm before moving to next

#### **PHASE 3: Integration**
1. Combine all sub-task outputs
2. Verify work item completion
3. Check dependencies are satisfied

## Benefits for Small LLMs

### 1. **File-Level Granularity**
- LLM knows **exactly** which file to work on
- No confusion about where to put code
- Clear new vs. modify operations

### 2. **Detailed Prompts per Work Item**
- Each work item has its own specific instructions
- Acts as a mini-prompt tailored to that file
- Reduces context switching

### 3. **Dependency Management**
- Work items execute in correct order
- Dependencies explicitly tracked
- No circular dependencies possible

### 4. **Sub-Task Breakdown**
- Large work items broken into 3-5 sub-tasks
- Each sub-task is atomic and testable
- Validation happens per sub-task (early error detection)

### 5. **Incremental Progress**
- Complete one sub-task before next
- Checkpoint validation prevents cascading errors
- Easier to debug and iterate

## Example Workflow

### Input Request:
```
"Add user authentication to the API"
```

### Planner Output (Work Items):
```json
{
  "description": "Implement user authentication system",
  "mode": "coder",
  "work_items": [
    {
      "mode": "architect",
      "file_path": "docs/auth_design.md",
      "file_status": "new",
      "description": "Design authentication flow with JWT tokens, including registration, login, and token refresh",
      "dependencies": []
    },
    {
      "mode": "coder",
      "file_path": "src/auth/models.py",
      "file_status": "new",
      "description": "Create User model with password hashing using bcrypt and email validation",
      "dependencies": [0]
    },
    {
      "mode": "coder",
      "file_path": "src/auth/routes.py",
      "file_status": "new",
      "description": "Implement /register and /login endpoints with JWT token generation and error handling",
      "dependencies": [0, 1]
    },
    {
      "mode": "sdet",
      "file_path": "tests/test_auth.py",
      "file_status": "new",
      "description": "Write tests for auth endpoints covering registration, login, invalid credentials, and token validation",
      "dependencies": [1, 2]
    }
  ],
  "priority": "high"
}
```

### Executor Processing:

For **Work Item 2** (`src/auth/models.py`):

**Sub-task Breakdown:**
1. Import required libraries (bcrypt, sqlalchemy, validators)
2. Define User model class with fields (id, email, password_hash)
3. Implement password hashing method (set_password)
4. Implement password verification method (check_password)
5. Add email validation in constructor

**Implementation** (incremental):
```python
# Sub-task 1: Imports ✓
import bcrypt
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import validators

# Sub-task 2: Model definition ✓
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

# Sub-task 3: Password hashing ✓
def set_password(self, password: str):
    salt = bcrypt.gensalt()
    self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

# Sub-task 4: Password verification ✓
def check_password(self, password: str) -> bool:
    return bcrypt.checkpw(
        password.encode(), 
        self.password_hash.encode()
    )

# Sub-task 5: Email validation ✓
def __init__(self, email: str, password: str):
    if not validators.email(email):
        raise ValueError(f"Invalid email: {email}")
    self.email = email
    self.set_password(password)
```

**Verification:**
- ☑ Sub-task 1: Complete - All imports present
- ☑ Sub-task 2: Complete - User model defined with all fields
- ☑ Sub-task 3: Complete - Password hashing implemented with bcrypt
- ☑ Sub-task 4: Complete - Password verification implemented
- ☑ Sub-task 5: Complete - Email validation in constructor

### Integration Check:
- Work item 2 complete ✓
- Dependencies satisfied (work item 0 completed) ✓
- Ready for work item 3 ✓

## Special File Paths

### 1. Console Output (`"console"`)
For peer/consulting mode with no file output:
```json
{
  "mode": "peer",
  "file_path": "console",
  "file_status": "new",
  "description": "Explain the difference between REST and GraphQL APIs with examples"
}
```

### 2. Documentation (`"docs/*.md"`)
For architecture and design documents:
```json
{
  "mode": "architect",
  "file_path": "docs/architecture.md",
  "file_status": "new",
  "description": "Design microservices architecture for the e-commerce platform"
}
```

### 3. Tests (`"tests/test_*.py"`)
For test files:
```json
{
  "mode": "sdet",
  "file_path": "tests/test_api.py",
  "file_status": "existing",
  "description": "Add integration tests for new authentication endpoints"
}
```

## Validation & Quality Control

### At Planner Level:
- ✅ Each work item has exact file path
- ✅ File status is valid (new/existing)
- ✅ Description is detailed and actionable
- ✅ Dependencies are valid indices
- ✅ No circular dependencies

### At Executor Level:
- ✅ Work items executed in dependency order
- ✅ Each work item broken into 3-5 sub-tasks
- ✅ Sub-tasks are atomic and testable
- ✅ Validation after each sub-task
- ✅ Integration check after work item

### At Reviewer Level:
- ✅ All work items completed
- ✅ Output matches file_path and file_status
- ✅ Code quality meets standards
- ✅ Tests pass (if applicable)

## Migration Guide

### For Existing Code Using Old Format:

**Old:**
```python
task_plan = {
    "steps": ["step 1", "step 2"],
    "relevant_files": ["file.py"]
}
```

**New:**
```python
task_plan = {
    "work_items": [
        {
            "mode": "coder",
            "file_path": "file.py",
            "file_status": "existing",
            "description": "Implement step 1 and step 2",
            "dependencies": []
        }
    ]
}
```

### Fallback Behavior:
If work_items is missing or empty, the system creates a default work item:
```python
{
    "mode": "coder",
    "file_path": "",
    "file_status": "existing",
    "description": "Implement the requested functionality",
    "dependencies": []
}
```

## Best Practices

### 1. **Granular Work Items**
- One file per work item (don't combine multiple files)
- Clear, specific descriptions
- Use dependencies to enforce order

### 2. **Appropriate Modes**
- `coder`: For implementation code
- `architect`: For design and architecture
- `sdet`: For tests and quality
- `peer`: For explanations and consultations

### 3. **File Status Accuracy**
- Use `"new"` only for files that don't exist
- Use `"existing"` for modifications
- Helps prevent accidental overwrites

### 4. **Dependency Management**
- List dependencies by index (0-based)
- Ensure no circular dependencies
- Order work items logically

### 5. **Detailed Descriptions**
- Include specific requirements
- Mention error handling needs
- Specify validation criteria

## Conclusion

The work item breakdown approach provides:
- **Clarity**: Each work item knows exactly what to do and where
- **Control**: Dependencies and execution order are explicit
- **Validation**: Sub-task breakdown ensures incremental verification
- **Quality**: Three-phase execution with checkpoints
- **Efficiency**: Optimized for small LLM context windows

This architecture enables small LLMs to handle complex tasks by breaking them into manageable, validated pieces with clear execution paths.
