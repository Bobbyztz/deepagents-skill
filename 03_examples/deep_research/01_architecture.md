# Deep Research: Architecture Deep Dive

> **📋 Prerequisites:** Read `00_overview.md`

---

## 🏗️ Three-Layer Architecture

Deep Research follows a **clean 3-layer design**:

```
┌─────────────────────────────────────────┐
│  Layer 1: Main Orchestrator            │  ← High-level coordination
│  - Plans research strategy              │
│  - Delegates to sub-agents              │
│  - Synthesizes results                  │
│  - Writes final report                  │
└─────────────────────────────────────────┘
             ↓ task() calls
┌─────────────────────────────────────────┐
│  Layer 2: Research Sub-agent(s)         │  ← Execution workers
│  - Execute web searches                 │
│  - Reflect after each search            │
│  - Return clean summaries               │
│  - Isolated contexts (parallel-safe)    │
└─────────────────────────────────────────┘
             ↓ tool calls
┌─────────────────────────────────────────┐
│  Layer 3: Tools                         │  ← Atomic operations
│  - tavily_search (web search)           │
│  - think_tool (reflection)              │
└─────────────────────────────────────────┘
```

---

## 🎯 Layer 1: Main Orchestrator

### Location

`deep_research/agent.py` lines 28-37, 54-59

### Configuration

```python
# System prompt (2 parts)
INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS +      # 6-step workflow
    SUBAGENT_DELEGATION_INSTRUCTIONS      # when to parallelize
)

agent = create_deep_agent(
    model=model,
    tools=[tavily_search, think_tool],    # Has tools...
    system_prompt=INSTRUCTIONS,           # ...but told NOT to use
    subagents=[research_sub_agent]        # Delegates instead
)
```

### Key Responsibilities

**1. Planning** (Step 1)

```python
write_todos([
    {"task": "Save request", "status": "in_progress"},
    {"task": "Research Python", "status": "pending"},
    {"task": "Research JavaScript", "status": "pending"},
    {"task": "Synthesize", "status": "pending"}
])
```

**2. Saving Request** (Step 2)

```python
write_file("/research_request.md", "Compare Python vs JavaScript...")
```

**3. Delegation** (Step 3)

```python
# For comparison query, calls task() multiple times:
task(subagent_type="research-agent", description="Research Python...")
task(subagent_type="research-agent", description="Research JavaScript...")
```

**4. Synthesis** (Step 4)

- Merge citations from sub-agents
- Consolidate findings
- Remove duplicate sources

**5. Report Writing** (Step 5)

```python
write_file("/final_report.md", formatted_report_with_citations)
```

**6. Verification** (Step 6)

```python
original = read_file("/research_request.md")
# Confirm: covered all aspects? citations correct?
```

### Constraints

**Hard limits** (from `agent.py`):

```python
max_concurrent_research_units = 3  # Max 3 parallel sub-agents
max_researcher_iterations = 3      # Max 3 delegation rounds
```

Injected into prompt via `.format()`.

---

## 🤖 Layer 2: Research Sub-agent

### Location

`deep_research/agent.py` lines 40-45

### Configuration

```python
research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search, think_tool]
}
```

### Execution Model

**Context Isolation:**

```python
# Sub-agent only sees:
messages = [
    {"role": "user", "content": "Research Python for web development"}
]

# Does NOT see main agent's planning, other sub-agents' work, etc.
```

**Typical Flow:**

```
1. tavily_search("Python web frameworks")
   → Returns 10k tokens of content

2. think_tool("Found Django/Flask. Need performance data")
   → Forces reflection

3. tavily_search("Python web performance")
   → Returns 12k tokens

4. think_tool("Have enough. 2 sources. Returning findings")
   → Decides to stop

5. Return summary with citations [1], [2]
```

### Hard Limits

**From RESEARCHER_INSTRUCTIONS prompt:**

```
- Simple queries: 2-3 searches max
- Complex queries: 5 searches max

Stop Immediately When:
- Can answer comprehensively
- Have 3+ sources
- Last 2 searches similar
```

### Output Format

Must return findings with inline citations:

```markdown
## Python for Web Development

Django is a full-stack framework [1]. Flask offers flexibility [2]...

### Sources

[1] Django Documentation: https://djangoproject.com/
[2] Flask Guide: https://flask.palletsprojects.com/
```

---

## 🛠️ Layer 3: Tools

### tavily_search

**Location:** `deep_research/research_agent/tools.py` lines 38-88

**Design Philosophy:** Tavily as URL discovery, not summaries

**Flow:**

```python
1. tavily_client.search(query) → Get URLs
2. For each URL:
   a. httpx.get(url) → Fetch content
   b. markdownify(html) → Convert to Markdown
3. Format as:
   ## Title
   **URL:** url
   [full markdown content]
   ---
```

**Why full content?**

- Preserves all information
- LLM decides what's important
- Avoids Tavily's summarization bias

### think_tool

**Location:** `deep_research/research_agent/tools.py` lines 91-116

**Implementation:**

```python
@tool
def think_tool(reflection: str) -> str:
    """Strategic reflection tool..."""
    return f"Reflection recorded: {reflection}"
```

**Just 1 line of logic!** Power is in:

1. Docstring (tells LLM when/how to use)
2. System prompt ("Use think_tool after EACH search")
3. Forcing a pause (LLM must formulate reflection)

---

## 🔄 Information Flow

### Complete Request Lifecycle

```
User Query
   ↓
Main Agent State: {messages: [], files: {}, todos: []}
   ↓
1. write_todos → State: {todos: [updated]}
   ↓
2. write_file("/research_request.md") → State: {files: {"/research_request.md": ...}}
   ↓
3. task() calls (parallel) →
      Sub-agent 1 State (isolated): {messages: [task description]}
         ↓
      tavily_search → ToolMessage (10k tokens)
         ↓
      think_tool → ToolMessage ("Reflection...")
         ↓
      ... more searches ...
         ↓
      Final AIMessage (summary with [1],[2])
         ↓
      Returned to main agent as ToolMessage

   (Sub-agent 2 runs in parallel, same pattern)
   ↓
Main Agent receives both ToolMessages
   ↓
4. Synthesis logic (citation merging)
   ↓
5. write_file("/final_report.md") → State: {files: {"/final_report.md": ...}}
   ↓
6. Verification (read "/research_request.md")
   ↓
Final AIMessage to user
```

---

## 🎨 Why This Architecture Works

### 1. Separation of Concerns

- **Orchestrator**: Strategy, synthesis, verification
- **Sub-agent**: Tactical execution (searches)
- **Tools**: Atomic operations

**No overlap** → clear responsibilities.

### 2. Context Isolation

- Main agent: ~10 messages (clean)
- Each sub-agent: ~50 messages (messy, but isolated)
- Main only sees summaries

**Result**: Efficient token usage.

### 3. Parallelization

- Multiple task() calls in single response
- LangGraph auto-executes in parallel
- Independent sub-agent contexts → safe concurrency

**Result**: Fast for comparisons.

### 4. File System as State

- `/research_request.md`: Original query (for verification)
- `/final_report.md`: Output artifact
- Automatic: Large tool results → files

**Result**: Clean communication protocol.

---

## 📊 Context Size Analysis

**Without sub-agents** (all in main agent):

```
Messages:
1. User query (100 tokens)
2-20. Searches + reflections (60,000 tokens)
21. Final answer (500 tokens)

Total: ~60,600 tokens per LLM call
```

**With sub-agents** (current architecture):

```
Main Agent:
1. User query (100 tokens)
2-4. Planning + delegation (300 tokens)
5-6. Sub-agent summaries (1,000 tokens combined)
7. Final answer (500 tokens)

Total: ~1,900 tokens per LLM call  ← 30× smaller!

Sub-agents (isolated, don't affect main):
Searches + reflections (60,000 tokens, but separate)
```

**Savings**: Main agent calls are **97% cheaper**.

---

## 🔗 Next Steps

**File-by-file code walkthrough:**
→ `02_file_walkthrough.md`

**Complete execution trace:**
→ `03_execution_flow.md`

**Prompt engineering details:**
→ `04_prompt_system.md`
