# Add Long-term Memory

> **📋 Prerequisites:**
>
> - `01_create_orchestrator.md`
> - `04_setup_filesystem.md`
> - `08_add_persistence.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

### LangGraph Memory Store

```python
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
import uuid

# Create store for cross-thread memory
store = InMemoryStore()

# Create checkpointer for within-thread state
checkpointer = MemorySaver()

# Compile with both
graph = builder.compile(checkpointer=checkpointer, store=store)

# In your node, access the store
def my_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")

    # Save a memory
    memory_id = str(uuid.uuid4())
    store.put(namespace, memory_id, {"preference": "likes coffee"})

    # Retrieve memories
    memories = store.search(namespace)
    return {"memories": [m.value for m in memories]}
```

---

## 📖 Checkpointer vs Store

| Feature       | Checkpointer       | Store                   |
| ------------- | ------------------ | ----------------------- |
| **Scope**     | Within thread      | Across threads          |
| **Use**       | Conversation state | User preferences, facts |
| **Data**      | Messages, state    | Arbitrary key-value     |
| **Retrieval** | By thread_id       | By namespace + search   |

---

## 🎯 Memory Store Usage

### Basic Operations

```python
from langgraph.store.memory import InMemoryStore
import uuid

store = InMemoryStore()

# Namespace: (user_id, memory_type)
namespace = ("user-123", "preferences")

# PUT: Save memory
memory_id = str(uuid.uuid4())
store.put(namespace, memory_id, {"food": "pizza"})

# SEARCH: Retrieve memories
memories = store.search(namespace)
for m in memories:
    print(m.value)  # {"food": "pizza"}

# GET: Retrieve specific memory
memory = store.get(namespace, memory_id)
```

### Semantic Search

```python
from langchain.embeddings import init_embeddings

store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "dims": 1536,
        "fields": ["content"]
    }
)

# Store with content
store.put(namespace, str(uuid.uuid4()), {"content": "User prefers Italian food"})

# Semantic search
results = store.search(namespace, query="What food does user like?", limit=3)
```

---

## 🔄 Using in LangGraph

### In Node Functions

```python
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig

def memory_node(state, config: RunnableConfig, *, store: BaseStore):
    """Node that reads and writes memories."""
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "facts")

    # Read existing memories
    memories = store.search(namespace)
    facts = [m.value["fact"] for m in memories]

    # Potentially save new memory
    if state.get("new_fact"):
        store.put(namespace, str(uuid.uuid4()), {"fact": state["new_fact"]})

    return {"known_facts": facts}
```

### Compile with Store

```python
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

store = InMemoryStore()
checkpointer = MemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)

# Invoke with user_id
config = {
    "configurable": {
        "thread_id": "conv-123",
        "user_id": "user-456"
    }
}
result = graph.invoke(input, config)
```

---

## 🤝 With Deep Agents

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="...",
    store=store
)

# Use with config
config = {"configurable": {"thread_id": "t1", "user_id": "u1"}}
result = agent.invoke(input, config)
```

---

## 💾 Production: PostgreSQL Store

```python
# For production, use persistent store
# (Check LangGraph docs for PostgresStore implementation)
```

---

## 🔗 Next Steps

**Deep dive into memory:**
→ `04_langgraph_integration/04_memory_guide.md`

**Add persistence:**
→ `08_add_persistence.md`

---

## 💡 Key Takeaways

1. **Checkpointer** = within-thread state
2. **Store** = cross-thread memory
3. **Namespace** by user_id for isolation
4. **Semantic search** for intelligent retrieval
