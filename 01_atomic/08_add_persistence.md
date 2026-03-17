# Add Persistence (Checkpointer)

> **📋 Prerequisites:**
>
> - `01_create_orchestrator.md` or `00_quickstart/langgraph_quickstart.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.checkpoint.memory import MemorySaver

# Create checkpointer
checkpointer = MemorySaver()

# Compile graph with checkpointer
graph = builder.compile(checkpointer=checkpointer)

# Use with thread_id to persist state
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke(input, config)

# Subsequent calls with same thread_id continue the conversation
result2 = graph.invoke({"messages": [{"role": "user", "content": "What did I just say?"}]}, config)
```

---

## 📖 What is Persistence?

**Persistence** allows your graph to:

- ✅ Save state between invocations
- ✅ Resume conversations (memory)
- ✅ Enable human-in-the-loop workflows
- ✅ Support time-travel debugging
- ✅ Provide fault tolerance

**Key Concepts:**

- **Thread**: A unique conversation/session identified by `thread_id`
- **Checkpoint**: A snapshot of graph state at each super-step
- **Checkpointer**: The component that saves/loads checkpoints

---

## 🎯 Step-by-Step Guide

### Step 1: Choose a Checkpointer

```python
# === Option 1: In-Memory (Development) ===
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# === Option 2: SQLite (Local Persistence) ===
# pip install langgraph-checkpoint-sqlite
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
conn = sqlite3.connect("checkpoints.db")
checkpointer = SqliteSaver(conn)

# === Option 3: PostgreSQL (Production) ===
# pip install langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@localhost/db")
checkpointer.setup()  # Create tables
```

### Step 2: Compile Graph with Checkpointer

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# Add checkpointer here
graph = builder.compile(checkpointer=checkpointer)
```

### Step 3: Use Thread ID

```python
# Each thread is a separate conversation
config = {"configurable": {"thread_id": "conversation-123"}}

# First message
result1 = graph.invoke(
    {"messages": [{"role": "user", "content": "My name is Alice"}]},
    config
)

# Follow-up (same thread_id = same conversation)
result2 = graph.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config
)
# Agent will remember "Alice"
```

---

## 🔧 Working with State

### Get Current State

```python
# Get the latest state for a thread
config = {"configurable": {"thread_id": "user-123"}}
snapshot = graph.get_state(config)

print(snapshot.values)  # Current state values
print(snapshot.next)    # Next nodes to execute
```

### Get State History

```python
# Get all checkpoints for a thread
for snapshot in graph.get_state_history(config):
    print(f"Step: {snapshot.metadata['step']}")
    print(f"Values: {snapshot.values}")
```

### Update State Manually

```python
# Modify state (useful for human-in-the-loop)
graph.update_state(
    config,
    {"messages": [{"role": "user", "content": "Actually, call me Bob"}]},
    as_node="agent"  # Pretend this update came from the "agent" node
)
```

---

## 🔄 Time Travel

### Replay from Checkpoint

```python
# Get a specific checkpoint
for snapshot in graph.get_state_history(config):
    if snapshot.metadata['step'] == 2:
        checkpoint_id = snapshot.config['configurable']['checkpoint_id']
        break

# Replay from that checkpoint
replay_config = {
    "configurable": {
        "thread_id": "user-123",
        "checkpoint_id": checkpoint_id
    }
}
result = graph.invoke(None, replay_config)
```

### Fork from Checkpoint

```python
# Create a new branch from a specific checkpoint
graph.update_state(
    {"configurable": {"thread_id": "user-123", "checkpoint_id": checkpoint_id}},
    {"messages": [{"role": "user", "content": "Different path"}]}
)
```

---

## 🤝 With Deep Agents

Deep Agents can also use checkpointers:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="...",
    checkpointer=checkpointer  # Pass checkpointer here
)

# Now agent has memory across invocations
config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke({"messages": [...]}, config)
```

---

## 🏭 Production Setup: PostgreSQL

```python
from langgraph.checkpoint.postgres import PostgresSaver

# From connection string
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:password@localhost:5432/mydb"
)
checkpointer.setup()  # Creates required tables

# Or from existing connection
import psycopg
conn = psycopg.connect("postgresql://...")
checkpointer = PostgresSaver(conn)

graph = builder.compile(checkpointer=checkpointer)
```

### Async PostgreSQL

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = await AsyncPostgresSaver.from_conn_string(
    "postgresql://user:password@localhost:5432/mydb"
)
await checkpointer.setup()

graph = builder.compile(checkpointer=checkpointer)

# Use with async
result = await graph.ainvoke(input, config)
```

---

## 🔐 Encryption

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

# Reads key from LANGGRAPH_AES_KEY environment variable
serde = EncryptedSerializer.from_pycryptodome_aes()

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://...",
    serde=serde
)
```

---

## 🐛 Troubleshooting

### Error: "No thread_id provided"

```python
# ❌ Wrong
result = graph.invoke(input)

# ✅ Correct
config = {"configurable": {"thread_id": "some-id"}}
result = graph.invoke(input, config)
```

### State not persisting

1. Check checkpointer is passed to `compile()`
2. Ensure same `thread_id` is used
3. For SQLite/Postgres, check database connection

### Memory growing too large

```python
# SQLite with WAL mode for better performance
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
checkpointer = SqliteSaver(conn)
```

---

## 🔗 Next Steps

**Add human-in-the-loop:**
→ `06_add_human_in_loop.md`

**Learn about Memory Store:**
→ `04_langgraph_integration/04_memory_guide.md`

**Time travel deep dive:**
→ `04_langgraph_integration/03_persistence_guide.md`

---

## 💡 Key Takeaways

1. **Checkpointers** enable state persistence across invocations
2. **Thread ID** is required for persistence to work
3. **InMemorySaver** for dev, **PostgresSaver** for production
4. Persistence enables **memory**, **human-in-the-loop**, and **time travel**
