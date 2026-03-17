# State Management Patterns

> **📋 Prerequisites:**
>
> - `01_atomic/10_graph_api_basics.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from typing_extensions import TypedDict, Annotated
import operator
from langgraph.graph import MessagesState

# === Pattern 1: Simple State ===
class SimpleState(TypedDict):
    value: str  # Overwrites on update

# === Pattern 2: With Reducer ===
class AccumulatingState(TypedDict):
    items: Annotated[list[str], operator.add]  # Appends on update

# === Pattern 3: Messages State ===
class ChatState(MessagesState):
    extra_field: str  # Extends built-in messages handling
```

---

## 📖 Key Concepts

### State = TypedDict

```python
class MyState(TypedDict):
    field1: str
    field2: int
    field3: list[str]
```

### Reducers = How Updates Merge

| Without Reducer    | With Reducer                     |
| ------------------ | -------------------------------- |
| `state["x"] = new` | `state["x"] = reducer(old, new)` |
| Overwrites         | Combines                         |

---

## 🎯 Pattern 1: Basic State (No Reducer)

```python
class State(TypedDict):
    current_step: str
    result: str

def node_a(state):
    return {"current_step": "a", "result": "A's result"}

def node_b(state):
    # Overwrites result from A
    return {"result": "B's result"}
```

**Use when**: Each node should replace the value completely.

---

## 🎯 Pattern 2: Accumulating State (With Reducer)

```python
from typing import Annotated
import operator

class State(TypedDict):
    # Each update appends to the list
    steps: Annotated[list[str], operator.add]

def node_a(state):
    return {"steps": ["A ran"]}

def node_b(state):
    return {"steps": ["B ran"]}

# After both: {"steps": ["A ran", "B ran"]}
```

**Use when**: Multiple nodes contribute to the same field (especially parallel).

---

## 🎯 Pattern 3: Messages State

```python
from langgraph.graph import MessagesState

class ChatState(MessagesState):
    """Built-in messages handling with reducer."""
    context: str  # Your additional fields

def chat_node(state):
    # messages automatically accumulated
    return {"messages": [AIMessage(content="Hello!")]}
```

**MessagesState includes**:

- `messages: Annotated[list[AnyMessage], add_messages]`
- Automatic message deduplication by ID
- Handles message types (Human, AI, Tool, etc.)

---

## 🎯 Pattern 4: Overwrite Reducer

Force overwrite even when reducer exists:

```python
from langgraph.graph.state import Overwrite

class State(TypedDict):
    items: Annotated[list[str], operator.add]

def reset_node(state):
    # Overwrite instead of append
    return {"items": Overwrite(["fresh", "start"])}
```

---

## 🎯 Pattern 5: Custom Reducer

```python
def max_reducer(existing: int, new: int) -> int:
    return max(existing, new)

class State(TypedDict):
    high_score: Annotated[int, max_reducer]

# Updates keep the maximum value
```

---

## 📊 Reducer Reference

| Reducer              | Effect              | Use Case          |
| -------------------- | ------------------- | ----------------- |
| `operator.add`       | Concatenate lists   | Parallel results  |
| `add_messages`       | Smart message merge | Chat history      |
| `lambda a,b: b`      | Always overwrite    | Latest value only |
| `lambda a,b: a or b` | Keep non-None       | Default values    |
| Custom function      | Your logic          | Domain-specific   |

---

## 🔧 State Updates from Nodes

Nodes return partial updates, not full state:

```python
# ❌ WRONG: Returning full state
def bad_node(state):
    state["value"] = "new"
    return state

# ✅ CORRECT: Return only updates
def good_node(state):
    return {"value": "new"}
```

---

## 🔄 Input/Output Schemas

Restrict what goes in/out:

```python
class InputSchema(TypedDict):
    query: str

class OutputSchema(TypedDict):
    result: str

class InternalState(InputSchema, OutputSchema):
    intermediate: str  # Not exposed

builder = StateGraph(
    InternalState,
    input=InputSchema,
    output=OutputSchema
)
```

---

## 🐛 Common Issues

### Parallel Results Lost

```python
# ❌ BAD: No reducer
results: str  # Last parallel node wins!

# ✅ GOOD: With reducer
results: Annotated[list[str], operator.add]
```

### State Not Updating

```python
# ❌ BAD: Mutating state directly
def node(state):
    state["items"].append("new")  # Mutations don't persist!
    return state

# ✅ GOOD: Return new value
def node(state):
    return {"items": state["items"] + ["new"]}  # Or use reducer
```

---

## 🔗 Next Steps

**Graph API basics:**
→ `01_atomic/10_graph_api_basics.md`

**Complex topology:**
→ `../complex_topology/README.md`

---

## 💡 Key Takeaways

1. **State = TypedDict** flowing through graph
2. **Reducers** control how updates merge
3. **`Annotated[list, operator.add]`** for parallel collection
4. **Return partial updates**, not full state
5. Use **MessagesState** for chat applications
