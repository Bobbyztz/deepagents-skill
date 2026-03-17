# Add Streaming

> **📋 Prerequisites:**
>
> - `01_create_orchestrator.md` or `00_quickstart/langgraph_quickstart.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer: 5 Stream Modes

```python
# === 1. updates: State deltas after each node ===
for chunk in graph.stream(input, stream_mode="updates"):
    print(chunk)  # {'node_name': {'key': 'value'}}

# === 2. values: Complete state after each node ===
for chunk in graph.stream(input, stream_mode="values"):
    print(chunk)  # Full state dict

# === 3. messages: LLM token stream ===
for msg, metadata in graph.stream(input, stream_mode="messages"):
    print(msg.content, end="")  # Token by token

# === 4. custom: User-defined data ===
from langgraph.config import get_stream_writer
def my_node(state):
    writer = get_stream_writer()
    writer({"progress": "50%"})  # Custom data
    return state

for chunk in graph.stream(input, stream_mode="custom"):
    print(chunk)

# === 5. debug: Detailed execution trace ===
for chunk in graph.stream(input, stream_mode="debug"):
    print(chunk)
```

---

## 📖 Stream Modes Explained

| Mode       | Description                   | Use Case            |
| ---------- | ----------------------------- | ------------------- |
| `updates`  | State changes after each node | Monitor progress    |
| `values`   | Full state after each node    | Debug state flow    |
| `messages` | LLM tokens + metadata         | Chat UX             |
| `custom`   | User-defined data             | Progress bars, logs |
| `debug`    | Maximum detail                | Debugging           |

---

## 🎯 Detailed Examples

### Stream Mode: `updates`

Shows only what changed after each node:

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    topic: str
    joke: str

def refine_topic(state):
    return {"topic": state["topic"] + " and cats"}

def generate_joke(state):
    return {"joke": f"Joke about {state['topic']}"}

builder = StateGraph(State)
builder.add_node("refine", refine_topic)
builder.add_node("generate", generate_joke)
builder.add_edge(START, "refine")
builder.add_edge("refine", "generate")
builder.add_edge("generate", END)
graph = builder.compile()

for chunk in graph.stream({"topic": "dogs"}, stream_mode="updates"):
    print(chunk)
# Output:
# {'refine': {'topic': 'dogs and cats'}}
# {'generate': {'joke': 'Joke about dogs and cats'}}
```

### Stream Mode: `values`

Shows complete state after each node:

```python
for chunk in graph.stream({"topic": "dogs"}, stream_mode="values"):
    print(chunk)
# Output:
# {'topic': 'dogs'}
# {'topic': 'dogs and cats', 'joke': None}
# {'topic': 'dogs and cats', 'joke': 'Joke about dogs and cats'}
```

### Stream Mode: `messages`

Streams LLM tokens:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4o-mini")

def call_llm(state):
    response = model.invoke([{"role": "user", "content": state["topic"]}])
    return {"response": response.content}

# ... build graph with call_llm node ...

for msg, metadata in graph.stream({"topic": "Tell a joke"}, stream_mode="messages"):
    if msg.content:
        print(msg.content, end="", flush=True)
```

### Stream Mode: `custom`

Send custom data from nodes:

```python
from langgraph.config import get_stream_writer

def processing_node(state):
    writer = get_stream_writer()

    # Send progress updates
    writer({"status": "Starting processing..."})
    # ... do work ...
    writer({"status": "50% complete"})
    # ... more work ...
    writer({"status": "Done!"})

    return {"result": "processed"}

for chunk in graph.stream(input, stream_mode="custom"):
    print(chunk)
# Output:
# {'status': 'Starting processing...'}
# {'status': '50% complete'}
# {'status': 'Done!'}
```

---

## 🔄 Multiple Stream Modes

Combine modes for richer output:

```python
for mode, chunk in graph.stream(input, stream_mode=["updates", "custom"]):
    if mode == "updates":
        print(f"State update: {chunk}")
    elif mode == "custom":
        print(f"Custom: {chunk}")
```

---

## 🌳 Stream from Subgraphs

Include outputs from nested subgraphs:

```python
for chunk in graph.stream(
    input,
    stream_mode="updates",
    subgraphs=True  # Include subgraph outputs
):
    namespace, data = chunk
    print(f"From {namespace}: {data}")

# Output:
# From (): {'parent_node': {...}}
# From ('subgraph:abc123',): {'child_node': {...}}
```

---

## 🤝 With Deep Agents

Deep Agents support streaming too:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(model, tools, system_prompt)

# Stream updates
for chunk in agent.stream({"messages": [...]}, stream_mode="updates"):
    print(chunk)

# Stream LLM tokens
for msg, metadata in agent.stream({"messages": [...]}, stream_mode="messages"):
    print(msg.content, end="")
```

### Streaming from Deep Agent Nodes

When Deep Agent is a LangGraph node:

```python
# Main graph with Deep Agent node
builder = StateGraph(MainState)
builder.add_node("research", research_node)  # Uses Deep Agent
builder.add_edge(START, "research")

graph = builder.compile()

# Stream with subgraphs to see Deep Agent's internal streaming
for chunk in graph.stream(input, stream_mode="updates", subgraphs=True):
    print(chunk)
```

---

## ⚡ Async Streaming

```python
async for chunk in graph.astream(input, stream_mode="updates"):
    print(chunk)

# With messages
async for msg, metadata in graph.astream(input, stream_mode="messages"):
    print(msg.content, end="")
```

---

## 🎨 Advanced Patterns

### Filter LLM Tokens by Node

```python
for msg, metadata in graph.stream(input, stream_mode="messages"):
    # Only show tokens from specific node
    if metadata["langgraph_node"] == "generate_joke":
        print(msg.content, end="")
```

### Filter by LLM Tags

```python
# Tag your models
joke_model = init_chat_model("gpt-4o-mini", tags=["joke"])
serious_model = init_chat_model("gpt-4o-mini", tags=["serious"])

# Filter by tag
for msg, metadata in graph.stream(input, stream_mode="messages"):
    if "joke" in metadata.get("tags", []):
        print(msg.content, end="")
```

### Stream Custom Data from Tools

```python
from langchain.tools import tool
from langgraph.config import get_stream_writer

@tool
def search_database(query: str) -> str:
    """Search the database."""
    writer = get_stream_writer()

    writer({"progress": "Connecting to database..."})
    # ... connect ...

    writer({"progress": "Executing query..."})
    # ... query ...

    writer({"progress": "Found 100 results"})
    return "results..."
```

---

## 🐛 Troubleshooting

### No streaming output

1. Make sure you're iterating over the stream:

   ```python
   # ❌ Wrong
   result = graph.stream(input)

   # ✅ Correct
   for chunk in graph.stream(input):
       print(chunk)
   ```

2. Check stream_mode is valid

### LLM tokens not streaming

1. Ensure LLM is called within a node
2. Use `stream_mode="messages"`
3. For Python < 3.11 async, pass config explicitly

### Custom stream not working

1. Use `get_stream_writer()` in node
2. Use `stream_mode="custom"`

---

## 🔗 Next Steps

**Deep dive into streaming:**
→ `04_langgraph_integration/05_streaming_guide.md`

**Add persistence for stateful streaming:**
→ `08_add_persistence.md`

**Combine with human-in-the-loop:**
→ `06_add_human_in_loop.md`

---

## 💡 Key Takeaways

1. **5 stream modes**: `updates`, `values`, `messages`, `custom`, `debug`
2. **`messages`** for LLM token streaming
3. **`custom`** for user-defined progress/status
4. **`subgraphs=True`** to include nested graph outputs
5. Can combine multiple modes
