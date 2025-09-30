# Vivek TODO List - Small LLM Optimized

Comprehensive improvement roadmap to make Vivek a truly excellent AI coding assistant that works effectively with small LLMs (1B-3B parameters).

> **🚨 PRIORITY SHIFT:** Small LLM optimization is now Phase 1, followed by LangGraph integration. This solves fundamental context window and capability limitations before building advanced features.

---

## 🔥 Phase 1: Critical Foundation - Small LLM Optimization (Week 1-2)

### 1. Model & Context Optimization for Small LLMs ⭐ **NEW #1 PRIORITY**
**Priority:** Critical (Highest)
**Status:** In Progress
**Impact:** Makes entire system viable for 1B-3B parameter models
**Location:** Core LLM infrastructure

**Why This is Now #1:**
Small LLMs have fundamental limitations that must be addressed first:
- ✅ **Context Windows:** 4K-8K tokens vs 128K for large models
- ✅ **Model Capabilities:** Simpler reasoning, more failures
- ✅ **Resource Constraints:** Limited memory and processing
- ✅ **Cost Effectiveness:** Can run on consumer hardware

**Core Optimizations:**
- **Model Selection**: Switch from `qwen2.5-coder:7b` to smaller 1B-3B models
- **Context Management**: External memory store + RAG implementation
- **Prompt Engineering**: Compress all prompts to fit small context windows
- **Generation Parameters**: Optimize temperature and token limits for small models

**Tasks:**
- [x] **Implement external memory store for long-term context management**
- [x] **Add RAG (Retrieval-Augmented Generation) for context injection**
- [ ] Update model selection to use smaller 1B-3B parameter models
- [ ] Optimize prompts for 4K-8K token context windows
- [ ] Adjust temperature (0.3-0.7) and token limits (512-1024) for small LLMs
- [ ] Implement robust fallback mechanisms for model failures
- [ ] Simplify JSON parsing and add better error handling
- [ ] Add context prioritization and compression
- [ ] Test and validate changes with small LLM models

**Model Configuration:**
```python
# Optimized for small LLMs
class SmallLLMProvider(LLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        # Context window awareness
        if len(prompt) > 4000:  # Conservative limit
            prompt = self._compress_prompt(prompt)

        return ollama.generate(
            model=self.model_name,  # 1B-3B models only
            prompt=prompt,
            options={
                "temperature": 0.3-0.7,  # Higher for small models
                "top_p": 0.9,
                "num_predict": 512-1024,  # Smaller limits
                "repeat_penalty": 1.2
            }
        )
```

**External Memory Integration:**
```python
class ExternalMemoryStore:
    """Store conversation history and context externally"""
    def __init__(self, storage_path: str = ".vivek/memory.db"):
        self.storage = sqlite3.connect(storage_path)
        self._create_tables()

    def store_context(self, context_id: str, content: str, metadata: dict):
        # Store large context chunks externally
        pass

    def retrieve_relevant(self, query: str, limit_tokens: int) -> List[str]:
        # Retrieve only what's needed for current context
        pass
```

**Files to Create/Modify:**
- `vivek/llm/small_llm_provider.py` - Optimized provider for small models
- `vivek/core/external_memory.py` - External memory management
- `vivek/core/rag_context.py` - RAG implementation for context injection
- `vivek/llm/prompt_compressor.py` - Prompt optimization utilities
- `vivek/llm/models.py` - Add model capability detection

---

## 🔥 Phase 2: LangGraph Foundation (Week 3-4)

### 2. LangGraph Integration (Small LLM-Aware) ⭐ **ENHANCED FOR SMALL LLMS**
**Priority:** Critical
**Status:** Not Started
**Impact:** Provides orchestration foundation optimized for small model constraints

**Enhanced for Small LLMs:**
- **Memory-Efficient State**: Compressed state data, selective persistence
- **Context-Aware Nodes**: Nodes that respect context window limits
- **Smart Context Injection**: Use external memory + RAG instead of large state
- **Fallback Strategies**: Handle small model failures gracefully

**Tasks:**
- [ ] Build StateGraph with context window awareness
- [ ] Define memory-efficient state management
- [ ] Implement context-aware node functions (planner, executor, reviewer)
- [ ] Add conditional edges optimized for small model limitations
- [ ] Integrate efficient context injection system (uses Phase 1 RAG)
- [ ] Add fallback strategies for model failures
- [ ] Create compatibility layer with existing orchestrator
- [ ] Migrate tests for graph-based orchestration

**Small LLM-Optimized State:**
```python
class SmallLLMVivekState(TypedDict):
    user_input: str
    task_plan: dict  # Compressed, essential only
    executor_output: str
    context: dict    # External memory references, not full content
    memory_ids: List[str]  # References to external memory store
    model_capabilities: dict  # Track model limitations
```

---

## 🔥 Phase 3: Context-Aware Tools (Week 5-6)

### 3. File Operations with Small LLM Constraints
**Priority:** Critical
**Enhanced for Small LLMs:**
- **Intelligent File Selection**: Only load relevant files to avoid context overflow
- **Chunked Processing**: Handle large files in small chunks
- **Minimal Context Tools**: Tools designed for limited context windows

### 4. Project Analysis for Small Models
**Priority:** Critical
- **Efficient Analysis**: Parse only essential project information
- **Smart Indexing**: Build lightweight indexes that fit in memory
- **Context Compression**: Summarize project info for small models

---

## 🎯 Phase 4: Core Features (Week 7-10)

### 5. Review and Analyze Commands
**Priority:** High
**Small LLM Considerations:**
- **Simplified Prompts**: Use compressed, focused prompts
- **Progressive Disclosure**: Show complex information in stages
- **Smart Fallbacks**: Graceful degradation for complex analysis

### 6. Enhanced Error Handling for Small Models
**Priority:** High
**New Exception Types:**
```python
class ContextWindowExceededError(VivekError): pass
class ModelCapacityError(VivekError): pass
class PromptTooLargeError(VivekError): pass
```

---

## 📊 INTEGRATION BENEFITS

### **Small LLM Optimizations That Enhance LangGraph:**
1. **External Memory + RAG** → Context injection without state bloat
2. **Prompt Optimization** → More efficient graph nodes
3. **Fallback Mechanisms** → Better error recovery in graph
4. **Model Selection** → Appropriate model routing

### **LangGraph That Helps Small LLMs:**
1. **State Management** → Perfect for context window management
2. **Persistence** → Complements external memory store
3. **Human-in-the-loop** → Handles small model limitations
4. **Event Streaming** → Better UX for slower small models

---

## 🚀 IMPLEMENTATION SEQUENCE

**Week 1-2: Small LLM Foundation**
1. External memory store + RAG implementation ✅
2. Model selection and parameter optimization
3. Prompt compression across all components
4. Basic fallback mechanisms

**Week 3-4: LangGraph Integration**
1. Build StateGraph with context awareness
2. Implement memory-efficient state management
3. Add context injection systems
4. Enhanced error handling

**Week 5-8: Feature Development**
- All features build on optimized foundation
- Context constraints already addressed
- Better performance and reliability

---

## ✨ KEY INSIGHTS

1. **Small LLM optimization must come first** - fixes fundamental limitations
2. **External memory + RAG is the biggest win** - elegantly solves context problems
3. **LangGraph + small LLMs work excellently together** - state management complements context limits
4. **Most existing features become easier** - solid foundation enables everything

**Success Metrics for Small LLMs:**
- [ ] Models run effectively in 4K-8K context windows
- [ ] External memory store handles large contexts efficiently
- [ ] RAG provides relevant information without context overflow
- [ ] Graceful fallbacks when models struggle with complexity
- [ ] All existing functionality works with 1B-3B parameter models

---

## 🎯 REVISED ROADMAP ACCELERATION

**v0.1.5 (Small LLM Foundation):** Context optimization + basic LangGraph
**v0.2.0 (Context Master):** Full LangGraph + RAG + project analysis
**v0.3.0 (Cloud Hybrid):** Existing roadmap features on solid foundation
**v0.4.0 (Enterprise Ready):** Advanced features with small LLM reliability

This integrated approach gives you the **best of both worlds**: strategic LangGraph foundation + practical small LLM optimizations.