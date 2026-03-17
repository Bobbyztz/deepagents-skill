# Context Isolation Pattern

> **📋 Prerequisites:** `01_atomic/03_configure_subagent.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

**Problem**: Agent context grows too large (expensive, slow, may exceed limits)

**Solution**: Delegate to sub-agents that have isolated contexts

```python
# Orchestrator: Clean context (~100 tokens)
#    ↓ task() call
# Sub-agent: Messy context (50,000 tokens)
#    ↓ returns summary (~500 tokens)
# Orchestrator: Still clean (~600 tokens)
```

---

## 📖 Why Context Isolation?

### Without Isolation

```
User query
  ↓
Agent does 10 web searches
  ↓
Context: 50,000+ tokens 💸
  ↓
Every subsequent call includes all that context
```

### With Isolation

```
User query
  ↓
Orchestrator (minimal context)
  ↓ spawns sub-agent
Sub-agent (isolated, does 10 searches)
  ↓ returns summary
Orchestrator receives only the summary
  ↓
Context stays manageable ✅
```

---

## 🎯 Implementation

### Deep Agents Approach

```python
from deepagents import create_deep_agent

research_subagent = {
    "name": "researcher",
    "description": "Delegate research tasks. Give one topic at a time.",
    "system_prompt": "You are a researcher. Search thoroughly, then summarize.",
    "tools": [web_search, think_tool]
}

orchestrator = create_deep_agent(
    model=model,
    tools=[],
    system_prompt="""You are an orchestrator.

RULE: NEVER do research yourself. ALWAYS delegate to researcher.
""",
    subagents=[research_subagent]
)
```

### LangGraph Approach (Subgraph)

```python
from langgraph.graph import StateGraph, START, END

# Sub-graph with its own state
class ResearchState(TypedDict):
    topic: str
    findings: list[str]
    summary: str

def search(state):
    # Heavy work here - stays isolated
    return {"findings": ["Result 1", "Result 2", ...]}

def summarize(state):
    return {"summary": "Brief summary of findings"}

research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search)
research_builder.add_node("summarize", summarize)
research_builder.add_edge(START, "search")
research_builder.add_edge("search", "summarize")
research_builder.add_edge("summarize", END)
research_subgraph = research_builder.compile()

# Main graph uses subgraph as node
def research_node(state):
    result = research_subgraph.invoke({"topic": state["query"]})
    return {"research_summary": result["summary"]}  # Only summary!

main_builder = StateGraph(MainState)
main_builder.add_node("research", research_node)
```

---

## 📊 Benefits

| Metric     | Without Isolation       | With Isolation |
| ---------- | ----------------------- | -------------- |
| Token Cost | High (cumulative)       | Low (isolated) |
| Latency    | Increasing              | Stable         |
| Error Risk | High (context overflow) | Low            |
| Debugging  | Hard                    | Easy (modular) |

---

## 🎯 Best Practices

1. **Clear boundaries**: Each sub-agent has one responsibility
2. **Summary returns**: Sub-agents return summaries, not raw data
3. **No deep nesting**: Max 2 levels (orchestrator → sub-agent)
4. **File system for artifacts**: Store large outputs in files

---

## 🔗 Next Steps

**Configure sub-agents:**
→ `01_atomic/03_configure_subagent.md`

**Hybrid architecture:**
→ `../hybrid_architecture/README.md`

---

## 💡 Key Takeaways

1. **Context isolation** prevents token explosion
2. **Sub-agents** return **summaries**, not full context
3. Keep orchestrator **clean and focused**
4. Use **files** to pass large artifacts between agents
