# Streaming Complete Guide

> **📋 Prerequisites:** `01_atomic/09_add_streaming.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

Five stream modes for different use cases:

| Mode       | Output       | Use Case            |
| ---------- | ------------ | ------------------- |
| `updates`  | State deltas | Progress monitoring |
| `values`   | Full state   | Debugging           |
| `messages` | LLM tokens   | Chat UX             |
| `custom`   | User-defined | Progress bars       |
| `debug`    | Everything   | Debugging           |

---

## 📖 Basic Usage

```python
# Stream updates
for chunk in graph.stream(input, stream_mode="updates"):
    print(chunk)

# Multiple modes
for mode, chunk in graph.stream(input, stream_mode=["updates", "custom"]):
    print(f"{mode}: {chunk}")
```

---

## 🔧 Stream Modes

### updates

```python
for chunk in graph.stream(input, stream_mode="updates"):
    # {'node_name': {'field': 'value'}}
    print(chunk)
```

### values

```python
for chunk in graph.stream(input, stream_mode="values"):
    # Full state after each node
    print(chunk)
```

### messages

```python
for msg, metadata in graph.stream(input, stream_mode="messages"):
    # LLM tokens
    print(msg.content, end="")
```

### custom

```python
from langgraph.config import get_stream_writer

def my_node(state):
    writer = get_stream_writer()
    writer({"progress": "50%"})
    return state

for chunk in graph.stream(input, stream_mode="custom"):
    print(chunk)
```

---

## 🌳 Subgraph Streaming

Include nested graph outputs:

```python
for chunk in graph.stream(input, stream_mode="updates", subgraphs=True):
    namespace, data = chunk
    if namespace:
        print(f"Subgraph: {data}")
    else:
        print(f"Main: {data}")
```

---

## 🎨 Filtering

### By Node

```python
for msg, metadata in graph.stream(input, stream_mode="messages"):
    if metadata["langgraph_node"] == "target_node":
        print(msg.content)
```

### By LLM Tag

```python
model = init_chat_model("gpt-4", tags=["main"])

for msg, metadata in graph.stream(input, stream_mode="messages"):
    if "main" in metadata.get("tags", []):
        print(msg.content)
```

---

## ⚡ Async

```python
async for chunk in graph.astream(input, stream_mode="updates"):
    print(chunk)
```

---

## 🔗 Next Steps

→ `06_production_guide.md` - Production best practices
