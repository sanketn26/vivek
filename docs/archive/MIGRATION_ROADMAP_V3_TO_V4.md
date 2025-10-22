# Vivek Migration: v3.0.0 → v4.0.0 (Simplified & Realistic)

> ⚠️ **ARCHIVED**: This roadmap has been integrated into the workstream documents.
> Use the workstream structure for implementation (see V4_IMPLEMENTATION_INDEX.md).
> This document is kept for reference only.

**Document Type**: Implementation Roadmap (REFERENCE ONLY)
**Version**: 2.0
**Timeline**: 8 weeks (simplified from 12)
**Last Updated**: October 22, 2025
**Status**: ARCHIVED - See Workstreams

---

## Executive Summary

This roadmap outlines a **pragmatic 8-week plan** to migrate from v3.0.0 (simple orchestration) to v4.0.0 (intelligent dual-brain orchestration). The plan uses **vertical slices** to deliver working functionality incrementally, reducing integration risk.

### Key Changes from v1.0
- ✅ Reduced timeline: 12 weeks → 8 weeks
- ✅ Vertical slice approach (not component-by-component)
- ✅ Quantitative success metrics with baselines
- ✅ Minimal v4.0.0 scope (defer advanced features to v4.1.0+)
- ✅ Mode examples with concrete outputs
- ✅ Realistic weekly deliverables

### Core Transformation

```
v3.0.0                          v4.0.0
─────────────────────          ───────────────────────
Single LLM          →          Dual LLM (Planner/Executor)
1 output file       →          3-5 files with tests
No validation       →          Quality gate (0.75 threshold)
Heuristic tasks     →          LLM-based decomposition
No modes            →          2 modes (coder + sdet)
```

---

## Part 1: v3.0.0 Current State

### Architecture

```
User Request
    ↓
SimpleOrchestrator (keyword-based)
    ↓
Single LLM Call (Ollama)
    ↓
1 Code File
```

### Metrics (Baseline)

| Metric | v3.0.0 Current |
|--------|----------------|
| Files per request | 1 |
| Test file inclusion | 0% |
| Syntax errors | ~25% |
| Avg execution time | 12s |
| Token usage (avg) | 2.5k |
| Quality validation | None |
| User satisfaction (est.) | 6/10 |

### Limitations
- ❌ No intelligent decomposition
- ❌ Single monolithic output
- ❌ No quality validation
- ❌ No test generation
- ❌ Single provider only

---

## Part 2: v4.0.0 Target State (Minimal Scope)

### Architecture

```
User Request + Project Context
    ↓
DualBrainOrchestrator
    ├─ Planner (reasoning LLM)
    │  └─ Creates 3-5 work items with dependencies
    │
    ├─ Executor (code generation LLM)
    │  ├─ Mode: Coder (implementation)
    │  └─ Mode: SDET (tests)
    │
    └─ Quality Gate
       ├─ Completeness check
       ├─ Syntax validation
       └─ Decision: accept or iterate (max 1)

Output: 3-5 files (implementation + tests)
```

### Target Metrics (v4.0.0)

| Metric | v3.0.0 | v4.0.0 Target | How Measured |
|--------|--------|---------------|--------------|
| Files per request | 1 | 3-5 | Count generated files |
| Test inclusion | 0% | 80% | Count test files generated |
| Syntax errors | ~25% | <5% | Parse generated code |
| Avg execution time | 12s | 30-45s | End-to-end timing |
| Token usage (avg) | 2.5k | 6-8k | Track LLM API usage |
| Quality score | N/A | 0.75 avg | Quality service score |
| User satisfaction | 6/10 | 8/10 | Post-release survey |

### Deferred to v4.1.0+
- ⏭️ Architect mode (design docs)
- ⏭️ Peer mode (review)
- ⏭️ Parallel execution
- ⏭️ LangGraph integration
- ⏭️ Function calling
- ⏭️ Advanced caching
- ⏭️ Multiple providers (OpenAI, Anthropic)

---

## Part 3: 8-Week Implementation Plan (Vertical Slices)

### Overview: Vertical Slice Strategy

**NOT**: Build all components, integrate at end (risky)
**BUT**: Build end-to-end slices, add complexity gradually (safe)

```
Week 1-2: Minimal End-to-End (Working!)
Week 3-4: Add Quality Gate
Week 5-6: Add Complexity (Dependencies, SDET mode)
Week 7-8: Production Ready
```

---

### Week 1-2: Minimal End-to-End Slice

**Goal**: Working baseline (input → plan → execute → output)

#### Deliverables
1. **Simple Planner** (basic decomposition)
   - Input: User request
   - Output: 2-3 work items (no dependencies)
   - Mode: coder only
   - Single LLM provider (Ollama - already working)

2. **Basic Executor** (coder mode)
   - Execute work items sequentially
   - Generate code files
   - Write to disk

3. **Minimal Orchestrator**
   - Coordinate: plan → execute → save
   - No quality gate (yet)
   - No validation (yet)

4. **Work Item Model**
   ```python
   @dataclass
   class WorkItem:
       id: str
       file_path: str
       description: str
       mode: str = "coder"  # Only coder for now
   ```

5. **Integration Test**
   - Request: "Create simple FastAPI endpoint"
   - Expected: 2 files (endpoint + model)
   - Verify: Files created with reasonable content

#### Success Criteria
- ✅ End-to-end flow works
- ✅ Generates 2-3 files
- ✅ 15+ unit tests passing
- ✅ 1 integration test passing

#### Example Output (Week 1-2)

**Input**: "Create user login endpoint"

**Plan** (from planner):
```json
{
  "work_items": [
    {
      "id": "item_1",
      "file_path": "src/models/user.py",
      "description": "User Pydantic model with email and password",
      "mode": "coder"
    },
    {
      "id": "item_2",
      "file_path": "src/routes/auth.py",
      "description": "POST /login endpoint using User model",
      "mode": "coder"
    }
  ]
}
```

**Output**: 2 files created ✅

---

### Week 3-4: Add Quality Gate

**Goal**: Validate outputs, iterate on failures

#### Deliverables
1. **Quality Service** (2 criteria only)
   - **Completeness** (0.0-1.0): All requirements met
   - **Correctness** (0.0-1.0): No syntax errors

2. **Quality Prompt**
   - Scoring rubric for each criterion
   - Structured feedback generation

3. **Iteration Manager** (max 1 iteration)
   - If quality < 0.70: generate feedback, retry once
   - Track iterations

4. **Enhanced Orchestrator**
   - Add quality gate after execution
   - Decision logic: accept or iterate

5. **Validation Tools**
   - Python syntax checker (ast.parse)
   - Basic completeness check (LLM-based)

#### Success Criteria
- ✅ Quality scoring works
- ✅ Iteration triggered on low quality
- ✅ 25+ unit tests passing
- ✅ 3 integration tests passing

#### Quality Scoring Example

**Request**: "Create user CRUD endpoint"

**Output 1** (Score: 0.55 - Below threshold):
```python
# Missing: No validation, no error handling
@router.post("/users")
def create_user(email: str):
    return {"email": email}
```

**Feedback**: "Missing: input validation, type hints, error handling"

**Output 2** (Score: 0.80 - Pass):
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr

@router.post("/users", status_code=201)
def create_user(user: UserCreate):
    try:
        # TODO: Save to database
        return {"email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500)
```

**Decision**: Accept ✅

---

### Week 5-6: Add Complexity

**Goal**: Dependencies, SDET mode, project context

#### Deliverables
1. **Dependency Resolution**
   - Parse dependencies from work items
   - Topological sort for execution order
   - Sequential execution respecting order

2. **SDET Mode** (test generation)
   - New execution mode for tests
   - Test-specific prompt template
   - Target: 70%+ coverage

3. **Project Context Builder** (basic)
   - Detect language (Python only for v4.0.0)
   - Detect framework (FastAPI, Flask)
   - Extract file structure (1 level)
   - Include in planner prompt

4. **Enhanced Planner**
   - Now generates 3-5 items (up from 2-3)
   - Includes dependencies
   - Includes at least 1 test item (sdet mode)

5. **Configuration System**
   - YAML-based config
   - Provider settings (planner/executor)
   - Quality threshold setting

#### Success Criteria
- ✅ Dependencies resolved correctly
- ✅ Test files generated with >70% relevance
- ✅ Project context extracted and used
- ✅ 40+ unit tests passing
- ✅ 5 integration tests passing

#### Dependency Example

**Request**: "Create user registration with database"

**Plan** (with dependencies):
```json
{
  "work_items": [
    {
      "id": "item_1",
      "file_path": "src/models/user.py",
      "description": "User database model (SQLAlchemy)",
      "mode": "coder",
      "dependencies": []
    },
    {
      "id": "item_2",
      "file_path": "src/schemas/user.py",
      "description": "User Pydantic schemas (create, response)",
      "mode": "coder",
      "dependencies": ["item_1"]
    },
    {
      "id": "item_3",
      "file_path": "src/routes/register.py",
      "description": "POST /register endpoint",
      "mode": "coder",
      "dependencies": ["item_1", "item_2"]
    },
    {
      "id": "item_4",
      "file_path": "tests/test_register.py",
      "description": "Test registration endpoint (success + failures)",
      "mode": "sdet",
      "dependencies": ["item_3"]
    }
  ]
}
```

**Execution Order**: item_1 → item_2 → item_3 → item_4 ✅

---

### Week 7-8: Production Ready

**Goal**: Polish, testing, documentation, release

#### Deliverables
1. **Enhanced CLI**
   - Show real-time progress
   - Display quality scores
   - Colorized output (rich library)

2. **Error Handling**
   - Retry logic for LLM failures
   - Graceful degradation
   - Clear error messages

3. **Comprehensive Testing**
   - 100+ unit tests
   - 20+ integration tests
   - End-to-end scenarios:
     - Simple REST API
     - Database CRUD
     - Multi-file project

4. **Performance Optimization**
   - Profile hot paths
   - Optimize prompt token usage
   - Cache project context (5-min TTL)

5. **Documentation**
   - User guide (getting started)
   - Configuration guide
   - Mode guide (coder vs sdet)
   - Migration guide (v3 → v4)

6. **Release Preparation**
   - Version bump to 4.0.0
   - Release notes
   - Example projects
   - Tag and publish

#### Success Criteria
- ✅ 100+ tests, 85%+ coverage
- ✅ Execution time <45s for 5-file requests
- ✅ Documentation complete
- ✅ 3 working examples
- ✅ v4.0.0 released to PyPI

---

## Part 4: Mode-Specific Examples

### Coder Mode Output

**Request**: "Add user authentication to FastAPI app"

**Output**:
```python
# src/auth/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-here"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    """Handle authentication logic."""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
```

**Characteristics**:
- ✅ Production-ready
- ✅ Type hints
- ✅ Docstrings
- ✅ Error handling
- ✅ Security best practices

---

### SDET Mode Output

**Request**: "Write tests for authentication service"

**Output**:
```python
# tests/test_auth_service.py
import pytest
from datetime import timedelta
from jose import jwt
from auth.auth_service import AuthService, SECRET_KEY, ALGORITHM

@pytest.fixture
def auth_service():
    return AuthService()

class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_password_hash_and_verify_success(self, auth_service):
        """Test password hashing and successful verification."""
        plain = "SecurePassword123!"
        hashed = auth_service.get_password_hash(plain)

        assert auth_service.verify_password(plain, hashed)
        assert hashed != plain

    def test_wrong_password_fails_verification(self, auth_service):
        """Test that wrong password fails verification."""
        hashed = auth_service.get_password_hash("correct")
        assert not auth_service.verify_password("wrong", hashed)

    def test_empty_password_is_hashed(self, auth_service):
        """Test that empty password can be hashed (though not recommended)."""
        hashed = auth_service.get_password_hash("")
        assert hashed != ""
        assert auth_service.verify_password("", hashed)

class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token_with_default_expiry(self, auth_service):
        """Test token creation with default expiry."""
        data = {"sub": "user@example.com"}
        token = auth_service.create_access_token(data)

        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user@example.com"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiry(self, auth_service):
        """Test token creation with custom expiry time."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=60)
        token = auth_service.create_access_token(data, expires_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user@example.com"

    def test_expired_token_raises_error(self, auth_service):
        """Test that expired token raises JWTError."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = auth_service.create_access_token(data, expires_delta)

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_special_characters_in_password(self, auth_service):
        """Test password with special characters."""
        special_password = "P@ssw0rd!#$%^&*()"
        hashed = auth_service.get_password_hash(special_password)
        assert auth_service.verify_password(special_password, hashed)

    def test_very_long_password(self, auth_service):
        """Test very long password (72 chars is bcrypt limit)."""
        long_password = "a" * 72
        hashed = auth_service.get_password_hash(long_password)
        assert auth_service.verify_password(long_password, hashed)
```

**Characteristics**:
- ✅ 80%+ coverage
- ✅ Edge cases included
- ✅ Fixtures used
- ✅ Clear test names
- ✅ Grouped by functionality

---

## Part 5: Quality Scoring Rubric (Quantitative)

### Completeness (0.0-1.0)

| Score | Meaning | Example |
|-------|---------|---------|
| **1.0** | All requirements implemented, no gaps | FastAPI endpoint with validation, error handling, docstrings, type hints |
| **0.8** | Core features done, minor gaps | FastAPI endpoint with validation, missing some error cases |
| **0.6** | Major features done, some missing | FastAPI endpoint, basic validation, no error handling |
| **0.4** | Partial implementation | Basic endpoint skeleton, no validation |
| **0.2** | Minimal implementation | Function signature only |
| **0.0** | Nothing implemented | Empty file or irrelevant code |

### Correctness (0.0-1.0)

| Score | Meaning | Example |
|-------|---------|---------|
| **1.0** | No errors, passes all checks | Valid Python, correct imports, no undefined variables |
| **0.8** | Minor issues (style, warnings) | Valid but some linting warnings |
| **0.6** | Some errors, mostly fixable | 1-2 syntax errors or import errors |
| **0.4** | Multiple errors | 3-5 syntax errors |
| **0.2** | Many errors | 5+ errors, major issues |
| **0.0** | Completely broken | Cannot parse, wrong language |

### Example Scoring

**Request**: "Create FastAPI user CRUD endpoint"

**Output A** (Score: 0.95):
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user."""
    # TODO: Save to database
    return UserResponse(id=1, email=user.email, full_name=user.full_name)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID."""
    # TODO: Fetch from database
    if user_id < 1:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user_id, email="user@example.com", full_name="Test User")
```

**Scoring**:
- Completeness: 0.90 (has CREATE and READ, missing UPDATE/DELETE)
- Correctness: 1.00 (no errors, valid syntax)
- **Average: 0.95** ✅ Pass (threshold: 0.75)

---

**Output B** (Score: 0.55):
```python
@router.post("/users")
def create_user(email, name):
    return {"email": email, "name": name}
```

**Scoring**:
- Completeness: 0.40 (only CREATE, missing everything else)
- Correctness: 0.70 (valid but no types, no validation, no error handling)
- **Average: 0.55** ❌ Fail → Iterate with feedback

---

## Part 6: Configuration Structure (v4.0.0)

```yaml
# .vivek/config.yml

project_settings:
  name: "MyProject"
  languages: ["python"]
  frameworks: ["fastapi"]

llm_configuration:
  planner:
    provider: "ollama"
    model: "qwen2.5-coder:7b"
    temperature: 0.3
    max_tokens: 2048

  executor:
    provider: "ollama"
    model: "qwen2.5-coder:7b"
    temperature: 0.1
    max_tokens: 4096

  quality:
    threshold: 0.75
    max_iterations: 1
    enable_cache: true
    cache_ttl: 300

modes:
  coder:
    temperature: 0.1
    includes_tests: false

  sdet:
    temperature: 0.2
    test_coverage_target: 0.70
```

---

## Part 7: Testing Strategy

### Unit Tests (100+)

| Component | Tests | Coverage Target |
|-----------|-------|-----------------|
| Planner Service | 20 | 90%+ |
| Executor Service | 25 | 90%+ |
| Quality Service | 20 | 90%+ |
| Work Item Manager | 15 | 90%+ |
| Orchestrator | 20 | 85%+ |

### Integration Tests (20+)

**End-to-End Workflows** (10 tests):
1. Simple Python function → generates file
2. FastAPI REST endpoint → 2 files (endpoint + test)
3. Database CRUD → 3 files (model, schema, route)
4. Multi-file feature → 4-5 files
5. Error recovery → retry on failure

**Quality Gate** (5 tests):
1. Low quality → iteration triggered
2. Syntax error → rejected, retry
3. High quality → accepted immediately
4. Max iterations → fails gracefully
5. Threshold adjustment → affects decisions

**Dependency Resolution** (5 tests):
1. Linear dependencies → correct order
2. Tree dependencies → correct order
3. Circular dependencies → detected and rejected
4. No dependencies → any order
5. Complex graph → topological sort

### Performance Benchmarks (5 tests)

| Scenario | Target Time | Max Tokens |
|----------|-------------|------------|
| Simple (1-2 files) | <20s | <4k |
| Medium (3-4 files) | <35s | <8k |
| Complex (5 files) | <45s | <10k |
| With iteration | <60s | <12k |

---

## Part 8: Risk Mitigation

### Risk 1: Scope Creep
**Impact**: High
**Mitigation**:
- ✅ Strict v4.0.0 scope (2 modes only)
- ✅ Defer advanced features to v4.1.0+
- ✅ Weekly scope review

### Risk 2: Integration Issues
**Impact**: High
**Mitigation**:
- ✅ Vertical slice approach (always integrated)
- ✅ Integration tests from week 1
- ✅ Daily builds

### Risk 3: Quality Scoring Inaccuracy
**Impact**: Medium
**Mitigation**:
- ✅ Start with 2 criteria (not 4)
- ✅ Manual validation of scores
- ✅ Lower threshold initially (0.70 → 0.75)

### Risk 4: Timeline Slip
**Impact**: Medium
**Mitigation**:
- ✅ Buffer built in (8 weeks is conservative)
- ✅ MVP first, enhancements later
- ✅ Daily progress tracking

---

## Part 9: Success Checklist

### By End of Week 8

#### Functionality ✅
- [ ] Planner generating 3-5 work items
- [ ] Executor implementing coder + sdet modes
- [ ] Quality service scoring with 2 criteria
- [ ] Iteration working (max 1)
- [ ] Project context extracted
- [ ] Dependencies resolved

#### Code Quality ✅
- [ ] 100+ tests passing
- [ ] 85%+ coverage
- [ ] 0 critical bugs
- [ ] Performance acceptable (<45s)

#### Documentation ✅
- [ ] Getting started guide
- [ ] Configuration guide
- [ ] Mode guide
- [ ] Migration guide v3→v4

#### Release ✅
- [ ] Version 4.0.0
- [ ] PyPI published
- [ ] 3 working examples
- [ ] Release notes

---

## Part 10: v4.1.0 Roadmap (Deferred Features)

**Timeline**: 4 weeks after v4.0.0

### Planned Enhancements
1. **Additional Modes**
   - Architect mode (design docs, diagrams)
   - Peer mode (code review, suggestions)

2. **Parallel Execution**
   - Execute independent work items concurrently (max 3)
   - Reduce total execution time by 40%

3. **Multi-Provider Support**
   - OpenAI provider (GPT-4, GPT-3.5)
   - Anthropic provider (Claude family)
   - Provider fallback chains

4. **Advanced Quality**
   - Add 2 more criteria (best practices, test coverage)
   - Increase to 2 iterations max
   - Quality reports (JSON export)

5. **Enhanced Context**
   - Semantic file search (embeddings)
   - Multi-level file structure
   - Recent commits integration

---

## Part 11: Summary

### Key Differences from v1.0 Roadmap

| Aspect | v1.0 (12 weeks) | v2.0 (8 weeks) |
|--------|-----------------|----------------|
| **Approach** | Component-by-component | Vertical slices |
| **Modes** | 4 modes | 2 modes (coder + sdet) |
| **Providers** | 4 providers | 1 provider (Ollama) |
| **Parallel Execution** | Yes | No (deferred) |
| **LangGraph** | Optional | No (deferred) |
| **Function Calling** | Considered | No (deferred) |
| **Quality Criteria** | 4 | 2 (completeness + correctness) |
| **Iterations** | 2 max | 1 max |

### Why This is Better

1. **Faster Time to Value**: Working v4.0.0 in 8 weeks (not 12)
2. **Lower Risk**: Always integrated, not big-bang at end
3. **Gradual Complexity**: Simple → complex over time
4. **Realistic**: Based on actual development capacity
5. **Testable**: Integration tests from week 1
6. **Extensible**: Clean foundation for v4.1.0+

### Roadmap at a Glance

```
Week 1-2: Minimal End-to-End
├─ Planner (basic, 2-3 items)
├─ Executor (coder mode only)
├─ Orchestrator (no quality)
└─ Result: Working but no validation

Week 3-4: Add Quality Gate
├─ Quality service (2 criteria)
├─ Iteration logic (max 1)
├─ Decision engine
└─ Result: Validated outputs

Week 5-6: Add Complexity
├─ Dependency resolution
├─ SDET mode (tests)
├─ Project context
└─ Result: Multi-file with tests

Week 7-8: Production Ready
├─ CLI enhancement
├─ Error handling
├─ Testing (100+ tests)
├─ Documentation
└─ Result: v4.0.0 released ✅
```

---

**Document Status**: Complete (Simplified & Realistic)
**Version**: 2.0
**Last Updated**: October 22, 2025
**Ready for**: Week 1 Implementation
