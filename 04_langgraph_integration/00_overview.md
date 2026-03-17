# LangGraph Integration Overview

> **LangGraph Version**: `>=0.2.0`

---

## 🎯 What This Module Covers

This module provides comprehensive guides for LangGraph features and their integration with Deep Agents:

| Guide                        | Topic                                     |
| ---------------------------- | ----------------------------------------- |
| `01_graph_api_guide.md`      | StateGraph, nodes, edges, routing         |
| `02_functional_api_guide.md` | @entrypoint, @task decorators             |
| `03_persistence_guide.md`    | Checkpointers, state history, time travel |
| `04_memory_guide.md`         | Memory Store, cross-thread memory         |
| `05_streaming_guide.md`      | Stream modes, token streaming             |
| `06_production_guide.md`     | Deployment best practices                 |
| `07_migration_guide.md`      | Migrating to/from Deep Agents             |

---

## 📊 LangGraph Two APIs

### Graph API (Declarative)

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MyState)
builder.add_node("a", node_a)
builder.add_edge(START, "a")
builder.add_edge("a", END)
graph = builder.compile()
```

**Best for**: Complex workflows, team collaboration, visual debugging

### Functional API (Imperative)

```python
from langgraph.func import entrypoint, task

@task
def my_task(input): ...

@entrypoint()
def my_workflow(input):
    result = my_task(input).result()
    return result
```

**Best for**: Linear workflows, quick prototypes, existing code

---

## 🤝 Integration with Deep Agents

### Key Insight

```
create_deep_agent() returns CompiledStateGraph
                            ↓
           Can be used as LangGraph node!
```

### Recommended Architecture

```
LangGraph Main Graph (orchestration)
        │
        ├── Deep Agent Node 1 (complex task)
        ├── Deep Agent Node 2 (complex task)
        └── Regular Node (simple logic)
```

→ See `00_quickstart/deep_agent_as_node.md` for details

---

## 📖 Quick Reference

### Core Concepts

| Concept          | Description                       |
| ---------------- | --------------------------------- |
| **State**        | TypedDict flowing through graph   |
| **Node**         | Function that transforms state    |
| **Edge**         | Connection between nodes          |
| **Reducer**      | Controls how state updates merge  |
| **Checkpointer** | Persists state across invocations |
| **Store**        | Cross-thread memory storage       |

### Key Imports

```python
# Graph API
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

# Functional API
from langgraph.func import entrypoint, task

# Persistence
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# Advanced
from langgraph.types import Send, interrupt, Command
```

---

## 🔗 Learning Paths

### Quick Start

1. `01_graph_api_guide.md` - Core concepts
2. `05_streaming_guide.md` - Real-time output

### Full Integration

1. `01_graph_api_guide.md`
2. `03_persistence_guide.md`
3. `04_memory_guide.md`
4. `00_quickstart/deep_agent_as_node.md`

### Production Ready

1. All above +
2. `06_production_guide.md`
3. `07_migration_guide.md`

---

## 💡 Key Takeaways

1. **Two APIs**: Graph (declarative) and Functional (imperative)
2. **Deep Agents are LangGraph graphs** - seamless integration
3. **Persistence** enables memory and human-in-the-loop
4. **Streaming** improves UX significantly
