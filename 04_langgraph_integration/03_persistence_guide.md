# Persistence Complete Guide

> **📋 Prerequisites:** `01_atomic/08_add_persistence.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

Persistence enables:

- **Memory**: Continue conversations across invocations
- **Human-in-the-loop**: Pause and resume workflows
- **Time travel**: Replay and fork from any point
- **Fault tolerance**: Resume from failures

---

## 📖 Checkpointers

### InMemorySaver (Development)

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### SqliteSaver (Local)

```python
# pip install langgraph-checkpoint-sqlite
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect("checkpoints.db")
checkpointer = SqliteSaver(conn)
```

### PostgresSaver (Production)

```python
# pip install langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
)
checkpointer.setup()  # Create tables
```

---

## 🔧 Using Thread IDs

```python
# Thread = conversation/session
config = {"configurable": {"thread_id": "user-123"}}

# First message
result = graph.invoke({"messages": [HumanMessage("Hi")]}, config)

# Second message (same thread = remembers context)
result = graph.invoke({"messages": [HumanMessage("What's my name?")]}, config)
```

---

## 📊 State Operations

### Get Current State

```python
snapshot = graph.get_state(config)
print(snapshot.values)  # Current state
print(snapshot.next)    # Next nodes
```

### Get History

```python
for snapshot in graph.get_state_history(config):
    print(f"Step {snapshot.metadata['step']}: {snapshot.values}")
```

### Update State

```python
graph.update_state(
    config,
    {"messages": [HumanMessage("Override")]},
    as_node="agent"
)
```

---

## ⏰ Time Travel

### Replay from Checkpoint

```python
# Get checkpoint ID from history
for snapshot in graph.get_state_history(config):
    if snapshot.metadata['step'] == 2:
        checkpoint_id = snapshot.config['configurable']['checkpoint_id']
        break

# Replay from that point
replay_config = {
    "configurable": {
        "thread_id": "user-123",
        "checkpoint_id": checkpoint_id
    }
}
result = graph.invoke(None, replay_config)
```

### Fork (Branch)

```python
# Update at specific checkpoint creates new branch
graph.update_state(
    {"configurable": {"thread_id": "123", "checkpoint_id": "abc"}},
    {"messages": [HumanMessage("Different path")]}
)
```

---

## 🔐 Encryption

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

# Set LANGGRAPH_AES_KEY environment variable
serde = EncryptedSerializer.from_pycryptodome_aes()

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://...",
    serde=serde
)
```

---

## 🤝 With Deep Agents

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_deep_agent(
    model=model,
    tools=[...],
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke(input, config)
```

---

## 🔗 Next Steps

→ `04_memory_guide.md` - Cross-thread memory
→ `06_production_guide.md` - Production setup
