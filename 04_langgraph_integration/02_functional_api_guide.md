# Functional API Complete Guide

> **📋 Prerequisites:** `00_overview.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

The Functional API is LangGraph's **imperative** approach:

- Use standard Python control flow
- Minimal code changes to existing code
- `@entrypoint` for main workflow
- `@task` for durable steps

---

## ⚡ Quick Start

```python
from langgraph.func import entrypoint, task

@task
def research(query: str) -> dict:
    """A durable task."""
    # This runs as a separate step
    return {"findings": f"Research results for {query}"}

@task
def analyze(data: dict) -> dict:
    """Another durable task."""
    return {"analysis": f"Analysis of {data}"}

@entrypoint()
def my_workflow(query: str):
    """Main workflow entry point."""
    # Standard Python control flow!
    research_result = research(query).result()
    analysis_result = analyze(research_result).result()
    return analysis_result
```

---

## 📖 Core Concepts

### @entrypoint

```python
from langgraph.func import entrypoint
from langgraph.checkpoint.memory import MemorySaver

@entrypoint(checkpointer=MemorySaver())
def workflow(input_data):
    # Main workflow logic
    # Can use if/else, loops, etc.
    return result
```

Features:

- Entry point for the workflow
- Can have checkpointer for persistence
- Standard Python function

### @task

```python
from langgraph.func import task

@task
def my_task(data):
    # This is a durable step
    # Can be retried, persisted
    return result
```

Features:

- Returns immediately with Future-like object
- Call `.result()` to get actual result
- Enables persistence and retry

---

## 🔧 Patterns

### Sequential

```python
@entrypoint()
def sequential_workflow(query):
    step1 = task_a(query).result()
    step2 = task_b(step1).result()
    step3 = task_c(step2).result()
    return step3
```

### Conditional

```python
@entrypoint()
def conditional_workflow(query):
    category = classify(query).result()

    if category == "code":
        return handle_code(query).result()
    elif category == "research":
        return handle_research(query).result()
    else:
        return handle_general(query).result()
```

### Parallel

```python
@entrypoint()
def parallel_workflow(items):
    # Start all tasks
    futures = [process_item(item) for item in items]

    # Wait for all results
    results = [f.result() for f in futures]

    return combine(results).result()
```

### Loop

```python
@entrypoint()
def iterative_workflow(query):
    result = initial_process(query).result()

    while not is_good_enough(result):
        result = refine(result).result()

    return result
```

---

## 📊 Graph API vs Functional API

| Aspect           | Graph API   | Functional API |
| ---------------- | ----------- | -------------- |
| Style            | Declarative | Imperative     |
| Control Flow     | Edges       | if/for/while   |
| Visualization    | Excellent   | Limited        |
| Team Collab      | Better      | Simpler        |
| Existing Code    | Harder      | Easier         |
| Complex Topology | Better      | Possible       |

---

## 🔄 With Deep Agents

```python
from deepagents import create_deep_agent
from langgraph.func import entrypoint, task

research_agent = create_deep_agent(model, tools, prompt)

@task
def do_research(query):
    result = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

@entrypoint()
def workflow(query):
    research = do_research(query).result()
    # Continue processing...
    return final_result
```

---

## 🐛 Common Issues

### Forgot .result()

```python
# ❌ Wrong - returns Future, not result
result = my_task(data)

# ✅ Correct
result = my_task(data).result()
```

### Tasks not persisting

- Make sure to use `@task` decorator
- Add checkpointer to `@entrypoint`

---

## 🔗 Next Steps

→ `01_graph_api_guide.md` - Alternative API
→ `03_persistence_guide.md` - State persistence
