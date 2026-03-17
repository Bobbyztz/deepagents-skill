# Configure Sub-agent

> **📋 Prerequisites:**
>
> - `01_create_orchestrator.md`
> - `02_add_tool.md`
> - `02_patterns/context_isolation/README.md` (recommended)
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from deepagents import create_deep_agent

# Define sub-agent configuration
research_subagent = {
    "name": "research-agent",
    "description": "Delegate research tasks to this agent. Give it one focused topic at a time.",
    "system_prompt": "You are a focused researcher. Use web_search to find information.",
    "tools": [web_search, think_tool]
}

# Create orchestrator with sub-agent
agent = create_deep_agent(
    model=model,
    tools=[],  # Orchestrator's tools (often empty)
    system_prompt="You are an orchestrator. Delegate research to the research-agent.",
    subagents=[research_subagent]
)
```

---

## 📖 Why Sub-agents?

### The Problem: Context Explosion

```
User asks complex question
  ↓
Agent does 10 web searches
  ↓
Context: 50,000+ tokens 💸
  ↓
Expensive, slow, may exceed limits
```

### The Solution: Context Isolation

```
User asks complex question
  ↓
Orchestrator (clean context, ~100 tokens)
  ↓ task() call
Sub-agent (isolated context, 50,000 tokens)
  ↓ returns summary (~500 tokens)
Orchestrator (still clean, ~600 tokens)
```

---

## 🎯 Sub-agent Configuration

### Required Fields

```python
subagent_config = {
    "name": "agent-name",        # Used in task() calls
    "description": "...",        # LLM reads this to know when to use
    "system_prompt": "...",      # Instructions for sub-agent
    "tools": [tool1, tool2]      # Tools the sub-agent can use
}
```

### Optional Fields

```python
subagent_config = {
    "name": "agent-name",
    "description": "...",
    "system_prompt": "...",
    "tools": [...],

    # Optional
    "model": different_model,    # Use different model for sub-agent
    "backend": shared_backend,   # Shared file system
}
```

---

## 🔄 How task() Works

When orchestrator calls `task()`:

```python
# Orchestrator calls:
task(
    agent="research-agent",
    task="Research quantum computing applications"
)

# Under the hood:
1. Sub-agent is instantiated
2. Receives the task as user message
3. Executes (may use tools, create files, etc.)
4. Returns summary to orchestrator
5. Sub-agent's full context is discarded
```

---

## 📊 Real-World Example: Research System

```python
from datetime import datetime

# Define tools
@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    # Implementation...

@tool
def think_tool(reflection: str) -> str:
    """Reflect on findings and plan next steps."""
    return f"Recorded: {reflection}"

# Sub-agent configuration
research_subagent = {
    "name": "research-agent",
    "description": """Delegate research tasks to this agent.

    Use for:
    - Web research on specific topics
    - Finding facts and statistics
    - Gathering multiple perspectives

    Give it ONE focused topic at a time.""",

    "system_prompt": f"""You are a focused researcher. Today is {datetime.now().strftime('%Y-%m-%d')}.

## Instructions
1. Use web_search to find information
2. After EACH search, use think_tool to reflect
3. Stop when you can answer confidently

## Output Format
Return findings with citations:
- Finding 1 [source URL]
- Finding 2 [source URL]
""",

    "tools": [web_search, think_tool]
}

# Orchestrator
orchestrator = create_deep_agent(
    model=model,
    tools=[],  # No tools - delegates everything
    system_prompt="""You are a research orchestrator.

## Workflow
1. Plan: Create TODO list
2. Delegate: Use task() to send research to sub-agents
3. Synthesize: Combine findings into final report
4. Save to /final_report.md

NEVER do research yourself - always delegate.""",

    subagents=[research_subagent]
)
```

---

## 🎨 Multiple Sub-agents

```python
# Specialist sub-agents
tech_researcher = {
    "name": "tech-researcher",
    "description": "Research technical topics, code, APIs",
    "system_prompt": "Focus on technical accuracy...",
    "tools": [web_search, code_search]
}

market_researcher = {
    "name": "market-researcher",
    "description": "Research market trends, business data",
    "system_prompt": "Focus on market analysis...",
    "tools": [web_search, data_analysis]
}

writer = {
    "name": "writer",
    "description": "Write polished reports from research findings",
    "system_prompt": "Write clear, structured reports...",
    "tools": [grammar_check]
}

# Orchestrator with multiple specialists
orchestrator = create_deep_agent(
    model=model,
    system_prompt="Coordinate research using specialist agents...",
    subagents=[tech_researcher, market_researcher, writer]
)
```

---

## ⚠️ Anti-Patterns

### ❌ Nesting Too Deep

```python
# BAD: Sub-agent has its own sub-agents
main → sub_agent_1 → sub_sub_agent → sub_sub_sub_agent

# GOOD: Flat structure with LangGraph for complex orchestration
# See: 00_quickstart/deep_agent_as_node.md
```

### ❌ Too Many Parallel Sub-agents

```python
# BAD: 10 parallel sub-agents
task("agent-1", "research A")
task("agent-2", "research B")
... # 10 times

# GOOD: Limit parallel agents
MAX_CONCURRENT = 3
```

---

## 🔗 Next Steps

**Understand context isolation:**
→ `02_patterns/context_isolation/README.md`

**Use Deep Agents in LangGraph:**
→ `11_use_deep_agent_as_node.md`

**Complex multi-agent systems:**
→ `02_patterns/complex_topology/README.md`

---

## 💡 Key Takeaways

1. **Sub-agents isolate context** - keep orchestrator clean
2. **Description is critical** - LLM reads it to decide when to delegate
3. **One focused task** per sub-agent call
4. **Avoid deep nesting** - use LangGraph for complex orchestration
