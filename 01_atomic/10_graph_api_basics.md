# Graph API Basics

> **📋 Prerequisites:**
>
> - `00_quickstart/langgraph_quickstart.md` (recommended)
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

# 1. Define State
class State(TypedDict):
    messages: Annotated[list, operator.add]  # reducer: append
    result: str

# 2. Define Nodes (functions)
def node_a(state: State):
    return {"result": "from A"}

def node_b(state: State):
    return {"messages": ["B processed"]}

# 3. Build Graph
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

# 4. Compile
graph = builder.compile()

# 5. Run
result = graph.invoke({"messages": [], "result": ""})
```

---

## 📖 Core Concepts

### State

State is a `TypedDict` that flows through the graph:

```python
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    # Simple field (overwrites on update)
    current_step: str

    # Field with reducer (appends on update)
    messages: Annotated[list, operator.add]

    # Optional field
    result: str | None
```

### Reducers

Reducers control how state updates merge:

```python
# Without reducer: OVERWRITES
class State(TypedDict):
    value: str  # state["value"] = new_value

# With reducer: COMBINES
class State(TypedDict):
    values: Annotated[list, operator.add]  # state["values"] += new_values
```

Built-in reducer for messages:

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    extra_field: str
```

### Nodes

Nodes are functions that read and update state:

```python
def my_node(state: State) -> dict:
    # Read from state
    current = state["value"]

    # Return updates (not full state!)
    return {"value": "updated"}
```

### Edges

Edges connect nodes:

```python
# Simple edge: A → B
builder.add_edge("a", "b")

# From START
builder.add_edge(START, "first_node")

# To END
builder.add_edge("last_node", END)
```

### Conditional Edges

Route based on state:

```python
from typing import Literal

def router(state: State) -> Literal["path_a", "path_b", "__end__"]:
    if state["should_continue"]:
        return "path_a"
    else:
        return END

builder.add_conditional_edges("decision_node", router)
```

---

## 🎯 Common Patterns

### Sequential Flow

```python
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

# Shorthand
builder.add_sequence([step_1, step_2, step_3])
builder.add_edge(START, "step_1")
```

### Conditional Branching

```python
def route(state: State) -> Literal["a", "b"]:
    if state["type"] == "a":
        return "a"
    return "b"

builder.add_edge(START, "classifier")
builder.add_conditional_edges("classifier", route)
builder.add_edge("a", END)
builder.add_edge("b", END)
```

### Parallel Execution (Fan-out/Fan-in)

```python
# Fan-out: Multiple edges from one source
builder.add_edge(START, "worker_1")
builder.add_edge(START, "worker_2")
builder.add_edge(START, "worker_3")

# Fan-in: Multiple edges to one target
builder.add_edge("worker_1", "aggregator")
builder.add_edge("worker_2", "aggregator")
builder.add_edge("worker_3", "aggregator")
builder.add_edge("aggregator", END)
```

Use reducer to combine results:

```python
class State(TypedDict):
    results: Annotated[list[str], operator.add]

def worker_1(state):
    return {"results": ["result from 1"]}

def worker_2(state):
    return {"results": ["result from 2"]}
```

### Loop with Exit Condition

```python
def should_continue(state: State) -> Literal["continue", "__end__"]:
    if state["iterations"] < 5:
        return "continue"
    return END

builder.add_edge(START, "process")
builder.add_conditional_edges("process", should_continue, {
    "continue": "process",  # Loop back
    END: END
})
```

---

## 🔧 Advanced Features

### Runtime Configuration

```python
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

class ContextSchema(TypedDict):
    model_name: str

def node(state: State, runtime: Runtime[ContextSchema]):
    model = runtime.context["model_name"]
    return {"result": f"Used {model}"}

builder = StateGraph(State, context_schema=ContextSchema)
# ...

graph.invoke(input, context={"model_name": "gpt-4"})
```

### Deferred Nodes

Wait for all incoming edges:

```python
builder.add_node("aggregator", aggregator_func, defer=True)
```

### Retry Policies

```python
from langgraph.types import RetryPolicy

builder.add_node(
    "api_call",
    api_call_func,
    retry_policy=RetryPolicy(max_attempts=3)
)
```

---

## 📊 Visualization

```python
# As PNG (requires mermaid)
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))

# As Mermaid text
print(graph.get_graph().draw_mermaid())
```

---

## 🔄 Command API

Combine state update + control flow:

```python
from langgraph.types import Command

def my_node(state: State) -> Command[Literal["next_a", "next_b"]]:
    return Command(
        update={"result": "processed"},
        goto="next_a"
    )
```

---

## 🐛 Common Issues

### State not updating

```python
# ❌ Wrong: Modifying state directly
def node(state):
    state["value"] = "new"  # Don't do this!
    return state

# ✅ Correct: Return update dict
def node(state):
    return {"value": "new"}
```

### Reducer not working

```python
# ❌ Wrong: Missing Annotated
class State(TypedDict):
    items: list

# ✅ Correct: Use Annotated with reducer
class State(TypedDict):
    items: Annotated[list, operator.add]
```

### Graph doesn't terminate

- Add conditional edge that returns `END`
- Or set recursion limit: `graph.invoke(input, {"recursion_limit": 10})`

---

## 🔗 Next Steps

**Add persistence:**
→ `08_add_persistence.md`

**Add streaming:**
→ `09_add_streaming.md`

**Complex topology patterns:**
→ `02_patterns/complex_topology/README.md`

**Use Deep Agent as node:**
→ `11_use_deep_agent_as_node.md`

---

## 💡 Key Takeaways

1. **State** flows through the graph
2. **Reducers** control how updates merge
3. **Nodes** return update dicts, not full state
4. **Conditional edges** enable dynamic routing
5. **Fan-out/Fan-in** for parallel execution
