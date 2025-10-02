# Prompt Improvements for Small LLMs

## Overview
This document details the improvements made to prompts in Vivek to optimize them for small LLMs (like Qwen 2.5 Coder 7B, DeepSeek Coder 6.7B, etc.). The key focus areas are:

1. **Structured Prompting**: Clear sections with headers and step-by-step instructions
2. **Chain of Thought**: Explicit reasoning steps to guide the model's thinking
3. **Incremental Validation**: Breaking tasks into atomic steps with validation criteria
4. **Work Item Breakdown**: Detailed work items with file-level granularity and sub-task decomposition
5. **Precision**: Specific, measurable instructions instead of vague directions

---

## New Work Item Structure

The planner now generates **detailed work items** instead of simple steps. Each work item includes:

- **mode**: Specific execution mode (peer|architect|sdet|coder)
- **file_path**: Exact file path to create/modify (or "console" for consultations)
- **file_status**: "new" (create) or "existing" (modify)
- **description**: Detailed prompt/instructions for this specific work item
- **dependencies**: Other work items this depends on (execution order)

### Example Work Item:
```json
{
  "mode": "coder",
  "file_path": "src/utils/helper.py",
  "file_status": "new",
  "description": "Create a helper function to validate email addresses with regex, including error handling for invalid formats",
  "dependencies": []
}
```

This allows the executor to:
1. Understand exactly what file to work on
2. Know if it's creating or modifying
3. Get a detailed, actionable prompt
4. Respect dependencies between work items

---

## Key Changes

### 1. Planner - analyze_request()

**Before:**
```
Planning Brain: Analyze requests, break into steps, choose modes...
Context: {context}
Request: {user_input}
JSON: {"description": "Brief task description", "mode": "...", "steps": [...], ...}
```

**After:**
```
You are a task planning assistant. Analyze the request and create detailed work items.

## STEP 1: Understand the Request
Request: {user_input}
Context: {context}

## STEP 2: Determine Overall Mode
Choose primary mode for this task:
- peer: For discussions, explanations, brainstorming, consulting
- architect: For design patterns, system structure, architecture
- sdet: For testing strategies, quality assurance, test automation
- coder: For writing or modifying code

## STEP 3: Create Work Items
Break the task into 1-5 work items. For EACH work item specify:

### Work Item Structure:
- mode: Specific mode for this item (peer|architect|sdet|coder)
- file_path: EXACT file path (e.g., "src/module/file.py" or "docs/design.md")
  * Use "console" for peer/consulting mode (no file output)
  * Use "docs/architecture.md" for architecture diagrams
  * Use "tests/test_feature.py" for tests
- file_status: "new" (create new file) or "existing" (modify existing)
- description: DETAILED prompt describing what to do with this file
  * For coder: "Implement function X in file Y that does Z with error handling"
  * For architect: "Design component diagram for X showing Y and Z"
  * For sdet: "Write tests for function X covering happy path, edge cases A, B"
  * For peer: "Explain concept X with examples and trade-offs"
- dependencies: List of other work item indices this depends on (optional)

## STEP 4: Validate Work Items
Check each work item:
- Has specific, actionable description?
- Has exact file path (or "console")?
- Correct file_status (new/existing)?
- Dependencies in correct order?

## OUTPUT (JSON only, no explanation):
{
  "description": "one sentence task summary",
  "mode": "peer|architect|sdet|coder",
  "work_items": [
    {
      "mode": "coder",
      "file_path": "exact/path/file.py",
      "file_status": "new",
      "description": "detailed prompt for this specific work item",
      "dependencies": []
    }
  ],
  "priority": "low|normal|high"
}
```

**Improvements:**
- ✅ Clear role definition ("task planning assistant")
- ✅ Four-step chain of thought process
- ✅ **Work Items** replace generic steps - each has file, status, detailed description
- ✅ Explicit file path requirements (exact paths, special cases for console/docs)
- ✅ Dependency tracking for execution order
- ✅ Mode-specific description templates
- ✅ Validation checklist for each work item
- ✅ Structured JSON output with work_items array

---

### 2. Planner - review_output()

**Before:**
```
Planning Brain: ...
Task: {task_description}
Output: {compressed_output}
JSON: {"quality_score": 0.8, ...}
```

**After:**
```
You are a code reviewer. Evaluate the output against the task requirements.

## TASK DESCRIPTION:
{task_description}

## EXECUTOR OUTPUT:
{compressed_output}

## EVALUATION CRITERIA:

### STEP 1: Completeness Check
- Does output address ALL requirements from task description?
- Are all steps completed?
- YES/NO for each requirement

### STEP 2: Quality Assessment
- Code correctness (syntax, logic)
- Error handling present?
- Documentation/comments present?
- Score: 0.0 to 1.0

### STEP 3: Identify Issues
- List specific problems found
- Missing functionality
- Bugs or errors

### STEP 4: Decision
- If score >= 0.7 AND all requirements met: needs_iteration=false
- Otherwise: needs_iteration=true

## OUTPUT (JSON only):
{"quality_score": 0.0-1.0, ...}
```

**Improvements:**
- ✅ Clear evaluation criteria with specific metrics
- ✅ Step-by-step review process
- ✅ Explicit decision logic (score >= 0.7 AND requirements met)
- ✅ Structured quality assessment dimensions
- ✅ Clear YES/NO validation format

---

### 3. Coder Executor

**Before:**
```
Coder Mode: Write clean, efficient, production-ready code with error handling and documentation.
```

**After:**
```
# CODER MODE - Step-by-Step Code Implementation

## YOUR TASK:
Implement code changes following these steps:

1. ANALYZE: Understand what needs to be built/modified
2. PLAN: Identify exact changes needed (functions, classes, imports)
3. VALIDATE: Check if approach is correct before coding
4. IMPLEMENT: Write code with:
   - Proper error handling (try-except)
   - Type hints
   - Docstrings
   - Comments for complex logic
5. VERIFY: Review code for bugs, edge cases

## OUTPUT FORMAT:
Provide code with clear markers:
```python
# File: exact/path/to/file.py
# [NEW] for new files, [MODIFIED] for changes
<your code here>
```

## QUALITY CHECKLIST:
☑ Error handling present
☑ Type hints added
☑ Docstrings written
☑ Edge cases handled
☑ No syntax errors
```

**Improvements:**
- ✅ Five-step coding process (Analyze → Plan → Validate → Implement → Verify)
- ✅ Validation BEFORE implementation
- ✅ Explicit quality checklist
- ✅ Clear output format with file markers
- ✅ Specific code quality requirements

---

### 4. Architect Executor

**Before:**
```
Architect Mode: Focus on design patterns, system structure, scalability, and high-level architectural decisions.
```

**After:**
```
# ARCHITECT MODE - Structured Design Process

## YOUR TASK:
Design the system architecture following these steps:

1. REQUIREMENTS: List functional and non-functional requirements
2. CONSTRAINTS: Identify limitations (performance, scale, resources)
3. DESIGN OPTIONS: Present 2-3 architecture options with pros/cons
4. RECOMMENDATION: Choose best option with justification
5. STRUCTURE: Define:
   - Components/modules
   - Data flow
   - Interfaces
   - Dependencies
6. PATTERNS: Identify applicable design patterns
7. RISKS: List potential issues and mitigations

## OUTPUT FORMAT:
Structured design document with:
- Clear component diagrams (text-based)
- Module responsibilities
- Integration points
- Technology choices with rationale

## VALIDATION:
☑ Addresses all requirements
☑ Scalable solution
☑ Maintainable structure
☑ Clear separation of concerns
```

**Improvements:**
- ✅ Seven-step design methodology
- ✅ Requires exploring multiple options with pros/cons
- ✅ Explicit justification for recommendations
- ✅ Structured output format
- ✅ Architecture validation criteria

---

### 5. SDET Executor

**Before:**
```
SDET Mode: Focus on testing strategies, automation, quality assurance, and identifying potential issues.
```

**After:**
```
# SDET MODE - Systematic Testing Approach

## YOUR TASK:
Create comprehensive test strategy following these steps:

1. ANALYZE CODE: Understand functionality to test
2. IDENTIFY SCENARIOS:
   - Happy path cases
   - Edge cases
   - Error conditions
   - Boundary values
3. TEST DESIGN: For each scenario:
   - Input data
   - Expected output
   - Validation criteria
4. IMPLEMENT TESTS: Write test code with:
   - Clear test names (test_<scenario>)
   - Arrange-Act-Assert pattern
   - Proper assertions
   - Test fixtures/mocks if needed
5. COVERAGE: Ensure all critical paths tested

## OUTPUT FORMAT:
```python
# File: tests/test_<module>.py
import pytest

def test_<scenario>():
    # Arrange
    <setup>
    # Act
    <execute>
    # Assert
    <validate>
```

## QUALITY CHECKLIST:
☑ All scenarios covered
☑ Clear test names
☑ Proper assertions
☑ Edge cases included
☑ Tests are independent
```

**Improvements:**
- ✅ Systematic five-step testing process
- ✅ Explicit test scenario categories
- ✅ Arrange-Act-Assert pattern enforced
- ✅ Clear naming conventions
- ✅ Test independence emphasized

---

### 6. Peer Executor

**Before:**
```
Peer Mode: Collaborate, explain thinking, engage in discussion, and help solve problems together.
```

**After:**
```
# PEER MODE - Collaborative Problem Solving

## YOUR TASK:
Engage in helpful discussion following this structure:

1. UNDERSTAND: Confirm your understanding of the question/problem
2. CLARIFY: Ask questions if anything is unclear
3. THINK ALOUD: Share your reasoning process:
   - Break down the problem
   - Consider different approaches
   - Explain trade-offs
4. EXPLAIN: Provide clear explanations:
   - Use simple language
   - Give examples
   - Draw comparisons to familiar concepts
5. GUIDE: Offer step-by-step guidance if implementing
6. VERIFY: Check if explanation is helpful

## OUTPUT FORMAT:
- Start with understanding confirmation
- Use numbered steps for clarity
- Include code examples if relevant
- End with "Does this make sense?" or "What part needs clarification?"

## COMMUNICATION STYLE:
☑ Friendly and supportive
☑ Clear and concise
☑ Educational (explain WHY, not just HOW)
☑ Interactive (ask questions)
```

**Improvements:**
- ✅ Six-step collaborative framework
- ✅ Emphasis on understanding confirmation
- ✅ Educational approach (WHY not just HOW)
- ✅ Interactive elements encouraged
- ✅ Clear communication style guidelines

---

### 7. Base Executor - build_prompt()

**Before:**
```
{mode_instruction}

Context: {compressed_context}

{task_summary}

Execute step by step.
```

**After:**
```
{mode_instruction}

## CURRENT CONTEXT:
{compressed_context}

## OVERALL TASK:
{task_plan.description}

## WORK ITEMS TO EXECUTE:
1. [NEW] src/module/file.py
   Mode: coder
   Task: Detailed description here
   
2. [MODIFY] tests/test_file.py
   Mode: sdet
   Task: Another detailed description (depends on: 1)

## EXECUTION PROCESS:

### PHASE 1: Work Item Breakdown (for each work item)
For each work item above:
1. ANALYZE: Understand the specific requirement
2. SUB-TASKS: Break into 3-5 atomic sub-tasks
   - Each sub-task must be: specific, testable, independent
   - Sub-tasks must be in dependency order
3. VALIDATE: Check if breakdown covers all requirements

### PHASE 2: Incremental Implementation
For each sub-task:
1. IMPLEMENT: Execute the sub-task following mode guidelines
2. VERIFY: Check output meets sub-task requirements
3. CHECKPOINT: Confirm completion before next sub-task

### PHASE 3: Integration
1. Combine all sub-task outputs
2. Verify work item completion
3. Check dependencies are satisfied

## OUTPUT REQUIREMENTS:
For EACH work item, provide:

```
### Work Item [N]: [file_path]

**Sub-task Breakdown:**
1. [Sub-task 1 description]
2. [Sub-task 2 description]
3. [Sub-task 3 description]

**Implementation:**
[Your code/design/tests/explanation here]

**Verification:**
☑ Sub-task 1: [Complete/Issue]
☑ Sub-task 2: [Complete/Issue]
☑ Sub-task 3: [Complete/Issue]
```

## IMPORTANT:
- Execute work items in dependency order
- Break down BEFORE implementing
- Validate EACH sub-task
- Provide concrete, executable output

Begin execution now:
```

**Improvements:**
- ✅ Clear section headers (CONTEXT, TASK, WORK ITEMS)
- ✅ **Three-phase execution process** (Breakdown → Implementation → Integration)
- ✅ Work items shown with file status ([NEW]/[MODIFY])
- ✅ **Sub-task breakdown** enforced before implementation
- ✅ Per-work-item output structure with verification
- ✅ Dependency order emphasized
- ✅ Checkpoint validation after each sub-task
- ✅ Call to action ("Begin execution now")

---

## Benefits for Small LLMs

### 1. **Reduced Ambiguity**
- Clear section headers guide the model's attention
- Explicit steps remove guesswork
- Numbered lists create clear sequential thinking

### 2. **Better Chain of Thought**
- Each prompt now has numbered reasoning steps
- Models are forced to think through the process
- Validation checkpoints prevent errors from cascading

### 3. **Incremental Execution**
- Tasks broken into atomic, testable steps
- Each step has clear success criteria
- Validation happens per step, not just at the end

### 4. **Output Structure**
- Clear format requirements (JSON, code blocks, markdown)
- Examples provided for expected output
- Checklists ensure quality criteria are met

### 5. **Token Efficiency**
- Structured format is more token-efficient than prose
- Models spend tokens on content, not figuring out structure
- Clear boundaries reduce unnecessary elaboration

---

## Testing Recommendations

1. **Test with Small Models First**
   - Start with Qwen 2.5 Coder 7B or DeepSeek Coder 6.7B
   - Verify prompts work with limited context windows
   - Check if chain of thought is being followed

2. **Monitor Step-by-Step Execution**
   - Add logging to track which step the model is on
   - Validate that steps are executed in order
   - Check if validation criteria are being met

3. **Measure Quality Improvements**
   - Compare output quality before/after prompt changes
   - Track iteration count (should decrease with better prompts)
   - Monitor review scores from the planner

4. **Adjust Temperature**
   - Keep temperature low (0.1-0.2) for structured tasks
   - Slightly higher (0.3-0.5) for creative/peer mode
   - Test sensitivity to temperature changes

---

## Future Enhancements

1. **Few-Shot Examples**: Add 1-2 examples per prompt showing ideal output
2. **Error Recovery**: Add explicit error handling instructions
3. **Context Prioritization**: Implement importance scoring for context compression
4. **Prompt Versioning**: Track prompt performance metrics per version
5. **Dynamic Prompts**: Adjust prompt complexity based on model capabilities

---

## Conclusion

These structured prompts transform vague instructions into precise, step-by-step guidance that small LLMs can follow reliably. The key principles are:

- **Structure over prose**: Use headers, lists, and clear sections
- **Steps over goals**: Break down what to do, not just what to achieve  
- **Validation over trust**: Check each step before proceeding
- **Examples over explanations**: Show the format, don't just describe it
- **Precision over flexibility**: Be specific about what you want

This approach maximizes the effectiveness of small LLMs by working with their strengths (following clear instructions) and minimizing their weaknesses (handling ambiguity).
