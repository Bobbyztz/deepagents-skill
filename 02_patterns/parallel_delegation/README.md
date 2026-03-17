# Parallel Delegation Pattern

> **📋 Prerequisites:**
>
> - `01_atomic/03_configure_subagent.md`
> - `../complex_topology/README.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

**When to parallelize**:

- Explicit comparisons: "Compare A vs B"
- Independent research topics
- Multiple perspectives needed

**When NOT to parallelize**:

- Sequential dependencies
- Simple questions
- Limited by rate limits

---

## 📖 Deep Agents: task() Parallelization

```python
system_prompt = """
## Delegation Strategy

**DEFAULT: Use 1 sub-agent** for most queries:
- "What is X?" → 1 sub-agent
- "Research topic Y" → 1 sub-agent

**ONLY use multiple parallel sub-agents for:**
- "Compare A vs B" → 2 parallel sub-agents
- "Compare A, B, C" → 3 parallel sub-agents
- "Get perspectives from tech, business, legal" → 3 parallel

## Limits
- Maximum 3 parallel sub-agents
"""
```

Agent naturally calls:

```python
task("researcher", "Research Python")
task("researcher", "Research JavaScript")  # Parallel!
```

---

## 📖 LangGraph: Fan-out / Fan-in

```python
import operator
from typing import Annotated

class State(TypedDict):
    query: str
    results: Annotated[list[str], operator.add]
    summary: str

def python_research(state):
    return {"results": ["Python findings..."]}

def javascript_research(state):
    return {"results": ["JavaScript findings..."]}

def combine(state):
    return {"summary": "\n".join(state["results"])}

builder = StateGraph(State)
builder.add_node("python", python_research)
builder.add_node("javascript", javascript_research)
builder.add_node("combine", combine)

# Fan-out
builder.add_edge(START, "python")
builder.add_edge(START, "javascript")

# Fan-in
builder.add_edge("python", "combine")
builder.add_edge("javascript", "combine")
builder.add_edge("combine", END)
```

---

## 🎯 Decision Framework

| Query Type                        | Parallel? | Reason                   |
| --------------------------------- | --------- | ------------------------ |
| "What is X?"                      | ❌        | Single topic             |
| "Compare X vs Y"                  | ✅        | Independent research     |
| "Research X then analyze"         | ❌        | Sequential dependency    |
| "Get tech, legal, business views" | ✅        | Independent perspectives |

---

## ⚠️ Pitfalls

1. **Over-parallelizing**: Not everything needs parallel
2. **Rate limits**: APIs may throttle parallel calls
3. **Cost**: More parallel = more tokens
4. **Merge complexity**: Results need proper aggregation

---

## 🔗 Next Steps

**Complex topology:**
→ `../complex_topology/README.md`

**Send API (dynamic parallel):**
→ `../send_api_patterns/README.md`

---

## 💡 Key Takeaways

1. **Parallelize for comparisons** and independent research
2. **Default to sequential** for simple queries
3. **Use reducers** to merge parallel results
4. **Limit parallel agents** (3 max recommended)
