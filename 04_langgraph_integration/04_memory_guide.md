# Memory Store Complete Guide

> **📋 Prerequisites:**
>
> - `01_atomic/07_add_long_term_memory.md`
> - `03_persistence_guide.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

| Feature      | Checkpointer       | Memory Store            |
| ------------ | ------------------ | ----------------------- |
| **Scope**    | Within thread      | **Across threads**      |
| **Use Case** | Conversation state | User preferences, facts |
| **Data**     | Graph state        | Key-value pairs         |
| **Search**   | By thread_id       | By namespace + query    |

---

## ⚡ Quick Answer

```python
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
import uuid

# Create store for cross-thread memory
store = InMemoryStore()

# In your node
def my_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")

    # Save memory
    store.put(namespace, str(uuid.uuid4()), {"fact": "User likes Python"})

    # Search memories
    memories = store.search(namespace)
    facts = [m.value["fact"] for m in memories]

    return {"known_facts": facts}

# Compile with store
graph = builder.compile(checkpointer=MemorySaver(), store=store)

# Invoke with user_id
config = {"configurable": {"thread_id": "t1", "user_id": "user-123"}}
result = graph.invoke(input, config)
```

---

## 📖 Core Operations

### PUT: Save Memory

```python
from langgraph.store.memory import InMemoryStore
import uuid

store = InMemoryStore()

# Namespace: tuple identifying the memory scope
namespace = ("user-123", "preferences")

# Save a memory
memory_id = str(uuid.uuid4())
store.put(namespace, memory_id, {"food": "pizza", "color": "blue"})
```

### SEARCH: Retrieve Memories

```python
# Get all memories in namespace
memories = store.search(namespace)

for memory in memories:
    print(memory.value)    # {"food": "pizza", "color": "blue"}
    print(memory.key)      # The memory_id
    print(memory.namespace)  # ("user-123", "preferences")
```

### GET: Retrieve Specific Memory

```python
# Get by key
memory = store.get(namespace, memory_id)
print(memory.value)
```

### DELETE: Remove Memory

```python
store.delete(namespace, memory_id)
```

---

## 🔍 Semantic Search

Enable meaning-based search with embeddings:

```python
from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore

store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "dims": 1536,
        "fields": ["content"]  # Fields to embed
    }
)

# Store with content
store.put(
    ("user-123", "facts"),
    str(uuid.uuid4()),
    {"content": "User prefers Italian food for dinner"}
)

# Semantic search
results = store.search(
    ("user-123", "facts"),
    query="What food does user like?",
    limit=5
)
```

---

## 🔧 Using in LangGraph Nodes

### Accessing Store in Nodes

```python
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig

def memory_node(state, config: RunnableConfig, *, store: BaseStore):
    """Node with store access."""
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")

    # Read existing memories
    memories = store.search(namespace)

    # Use memories in logic
    known_facts = [m.value["fact"] for m in memories]

    # Save new memory if needed
    if state.get("new_fact"):
        store.put(namespace, str(uuid.uuid4()), {"fact": state["new_fact"]})

    return {"context": "\n".join(known_facts)}
```

### Compiling with Store

```python
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

store = InMemoryStore()
checkpointer = MemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)

# Invoke with both thread_id and user_id
config = {
    "configurable": {
        "thread_id": "conversation-1",
        "user_id": "user-456"
    }
}
result = graph.invoke(input, config)
```

---

## 🎯 Common Patterns

### Pattern 1: User Preferences

```python
def preferences_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    prefs_ns = (user_id, "preferences")

    # Load preferences
    prefs = store.search(prefs_ns)
    pref_dict = {p.value["key"]: p.value["value"] for p in prefs}

    # Apply preferences
    response_style = pref_dict.get("response_style", "concise")

    return {"style": response_style}
```

### Pattern 2: Learning from Conversations

```python
def learn_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    facts_ns = (user_id, "learned_facts")

    # Extract facts from conversation
    last_message = state["messages"][-1].content

    if "my name is" in last_message.lower():
        name = extract_name(last_message)
        store.put(facts_ns, "name", {"fact": f"User's name is {name}"})

    return state
```

### Pattern 3: Cross-Conversation Context

```python
def context_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]

    # Get context from previous conversations
    context_ns = (user_id, "conversation_summaries")
    summaries = store.search(context_ns, limit=5)

    # Build context string
    prior_context = "\n".join([s.value["summary"] for s in summaries])

    return {"prior_context": prior_context}
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

# Memory persists across conversations for same user
config = {"configurable": {"thread_id": "t1", "user_id": "u1"}}
result = agent.invoke(input, config)
```

---

## 💾 Production: Persistent Store

For production, use a persistent backend:

```python
# PostgreSQL-backed store (check LangGraph docs for implementation)
# store = PostgresStore.from_conn_string("postgresql://...")
```

---

## 🐛 Troubleshooting

### Store not accessible in node

```python
# ❌ Wrong: Missing store parameter
def node(state, config):
    store.search(...)  # Error!

# ✅ Correct: Add *, store parameter
def node(state, config, *, store):
    store.search(...)  # Works!
```

### Memories not persisting

- InMemoryStore is ephemeral - use persistent store for production
- Check namespace consistency

---

## 🔗 Next Steps

**Persistence basics:**
→ `03_persistence_guide.md`

**Production deployment:**
→ `06_production_guide.md`

---

## 💡 Key Takeaways

1. **Store** = cross-thread memory (vs Checkpointer = within-thread)
2. **Namespace** by user_id for isolation
3. **Semantic search** with embeddings for intelligent retrieval
4. Access via `*, store` parameter in nodes
