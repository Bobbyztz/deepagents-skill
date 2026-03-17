# Graph API Complete Guide

> **📋 Prerequisites:** `01_atomic/10_graph_api_basics.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

The Graph API is LangGraph's **declarative** approach to building agents:

- Define state schema
- Add nodes (functions)
- Connect with edges
- Compile and run

---

## 📖 Core Components

### 1. State Definition

```python
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    # Simple field (overwrites)
    query: str

    # With reducer (accumulates)
    messages: Annotated[list, operator.add]

    # Optional
    result: str | None
```

### 2. Nodes

```python
def my_node(state: State) -> dict:
    """Node function signature."""
    # Read state
    query = state["query"]

    # Do work
    result = process(query)

    # Return UPDATES only
    return {"result": result}
```

### 3. Edges

```python
# Simple edge
builder.add_edge("a", "b")

# From START
builder.add_edge(START, "first")

# To END
builder.add_edge("last", END)

# Conditional
def router(state) -> Literal["a", "b"]:
    return "a" if state["condition"] else "b"

builder.add_conditional_edges("decision", router)
```

### 4. Compile

```python
graph = builder.compile()

# With checkpointer
from langgraph.checkpoint.memory import MemorySaver
graph = builder.compile(checkpointer=MemorySaver())
```

---

## 🔧 Advanced Features

### Reducers

```python
# Built-in
messages: Annotated[list, operator.add]

# Custom
def max_reducer(old, new):
    return max(old, new)

score: Annotated[int, max_reducer]

# Messages with dedup
from langgraph.graph import add_messages
messages: Annotated[list, add_messages]
```

### Input/Output Schemas

```python
class InputSchema(TypedDict):
    query: str

class OutputSchema(TypedDict):
    result: str

class InternalState(TypedDict):
    query: str
    intermediate: str  # Hidden from I/O
    result: str

builder = StateGraph(
    InternalState,
    input=InputSchema,
    output=OutputSchema
)
```

### Runtime Configuration

```python
def node(state, config):
    model = config["configurable"]["model"]
    # ...

result = graph.invoke(input, {"configurable": {"model": "gpt-4"}})
```

---

## 📊 Common Patterns

### ReAct Agent Loop

```python
def should_continue(state) -> Literal["tools", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")  # Loop
```

### Parallel Fan-out/Fan-in

```python
builder.add_edge(START, "worker_1")
builder.add_edge(START, "worker_2")
builder.add_edge("worker_1", "combine")
builder.add_edge("worker_2", "combine")
```

### Dynamic Branching (Send API)

```python
from langgraph.types import Send

def distribute(state):
    return [Send("worker", {"item": i}) for i in state["items"]]

builder.add_conditional_edges("distribute", distribute)
```

---

## 🐛 Common Issues

### State not updating

- Return dict with updates, not full state
- Check reducer if using lists

### Graph doesn't terminate

- Ensure conditional edge can return END
- Set recursion limit: `{"recursion_limit": 10}`

---

## 🔗 Next Steps

→ `02_functional_api_guide.md` - Alternative API
→ `03_persistence_guide.md` - State persistence
