# Send API Patterns (Dynamic Branching)

> **📋 Prerequisites:**
>
> - `../complex_topology/README.md`
> - `01_atomic/10_graph_api_basics.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.types import Send

def distribute_tasks(state):
    """Dynamically create parallel branches based on runtime data."""
    return [
        Send("worker", {"task": task})
        for task in state["tasks"]
    ]

builder = StateGraph(State)
builder.add_node("distribute", distribute_tasks)
builder.add_node("worker", worker_node)
builder.add_node("aggregate", aggregate_node)

builder.add_edge(START, "distribute")
builder.add_conditional_edges("distribute", distribute_tasks)  # Send API!
builder.add_edge("worker", "aggregate")
builder.add_edge("aggregate", END)
```

---

## 📖 When to Use Send API

| Static Fan-out           | Send API (Dynamic)     |
| ------------------------ | ---------------------- |
| Known at design time     | Known at runtime       |
| Fixed number of branches | Variable branches      |
| `add_edge(START, "a")`   | `Send("target", data)` |

**Use Cases:**

- Map-Reduce over dynamic data
- Processing variable-length lists
- Parallel API calls to multiple endpoints

---

## 🎯 Pattern 1: Map-Reduce

```python
from langgraph.types import Send
from typing import Annotated
import operator

class State(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]
    final: str

def map_items(state):
    """Create one Send per item."""
    return [Send("process_item", {"item": item}) for item in state["items"]]

def process_item(state):
    """Process single item."""
    return {"results": [f"Processed: {state['item']}"]}

def reduce_results(state):
    """Combine all results."""
    return {"final": " | ".join(state["results"])}

builder = StateGraph(State)
builder.add_node("map", map_items)
builder.add_node("process_item", process_item)
builder.add_node("reduce", reduce_results)

builder.add_edge(START, "map")
builder.add_conditional_edges("map", map_items)  # Returns Send objects
builder.add_edge("process_item", "reduce")
builder.add_edge("reduce", END)

graph = builder.compile()

# Usage
result = graph.invoke({"items": ["A", "B", "C"], "results": []})
# All items processed in parallel!
```

---

## 🎯 Pattern 2: Parallel Research

```python
def research_topics(state):
    """Create parallel research tasks."""
    topics = state["query"].split(",")  # "AI, ML, NLP" → ["AI", "ML", "NLP"]
    return [
        Send("researcher", {"topic": topic.strip()})
        for topic in topics
    ]

def researcher(state):
    """Research one topic."""
    # Each researcher is independent
    result = f"Research findings for: {state['topic']}"
    return {"findings": [result]}

def synthesize(state):
    """Combine all research."""
    all_findings = "\n".join(state["findings"])
    return {"report": f"## Combined Report\n{all_findings}"}

builder = StateGraph(ResearchState)
builder.add_node("distribute", research_topics)
builder.add_node("researcher", researcher)
builder.add_node("synthesize", synthesize)

builder.add_edge(START, "distribute")
builder.add_conditional_edges("distribute", research_topics)
builder.add_edge("researcher", "synthesize")
builder.add_edge("synthesize", END)
```

---

## 🎯 Pattern 3: With Deep Agents

```python
from deepagents import create_deep_agent
from langgraph.types import Send

research_agent = create_deep_agent(model, tools, "Research specialist")

def distribute(state):
    """Create parallel Deep Agent tasks."""
    return [
        Send("research_node", {"topic": topic})
        for topic in state["topics"]
    ]

def research_node(state):
    """Deep Agent processes one topic."""
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": f"Research: {state['topic']}"}]
    })
    return {"results": [result["messages"][-1].content]}
```

---

## 🔧 Send Object Details

```python
from langgraph.types import Send

# Basic Send
Send("target_node", {"key": "value"})

# Send with full state override
Send("target_node", {"entire": "new_state"})
```

**Important**: The dict passed to Send becomes the **input state** for that node instance.

---

## 📊 State with Reducers

Critical for collecting parallel results:

```python
from typing import Annotated
import operator

class State(TypedDict):
    # Without reducer - last write wins (bad for parallel!)
    bad_field: str

    # With reducer - appends all results (good!)
    results: Annotated[list, operator.add]
```

---

## ⚠️ Common Pitfalls

### No Reducer = Lost Data

```python
# ❌ BAD: Parallel writes overwrite each other
class State(TypedDict):
    result: str  # Last parallel branch wins!

# ✅ GOOD: Use reducer
class State(TypedDict):
    results: Annotated[list[str], operator.add]
```

### Forgetting Return from Distribute

```python
# ❌ BAD: Modifies state instead of returning Send
def distribute(state):
    for item in state["items"]:
        Send("worker", {"item": item})  # Does nothing!

# ✅ GOOD: Return list of Send
def distribute(state):
    return [Send("worker", {"item": item}) for item in state["items"]]
```

---

## 🔗 Next Steps

**Complex topology basics:**
→ `../complex_topology/README.md`

**Human-in-the-loop:**
→ `../human_in_loop/README.md`

---

## 💡 Key Takeaways

1. **Send API** for runtime-determined parallelism
2. **Return list of Send** from the distribute node
3. **Use reducers** to collect parallel results
4. Great for **Map-Reduce** and **variable-length processing**
