# Use Deep Agent as LangGraph Node【核心】

> **📋 Prerequisites:**
>
> - `00_quickstart/deep_agent_as_node.md`
> - `10_graph_api_basics.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from typing import TypedDict

# 1. Create Deep Agent
model = init_chat_model("anthropic:claude-sonnet-4-5-20250929")
research_agent = create_deep_agent(model, tools, "你是研究专家")

# 2. Define main graph state
class MainState(TypedDict):
    query: str
    result: str

# 3. Create wrapper node (state mapping)
def research_node(state: MainState) -> dict:
    # Input: MainState → Deep Agent format
    agent_result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    # Output: Deep Agent → MainState
    return {"result": agent_result["messages"][-1].content}

# 4. Build graph
builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_edge(START, "research")
builder.add_edge("research", END)
graph = builder.compile()

# 5. Use
result = graph.invoke({"query": "研究量子计算"})
```

---

## 📖 Why This Pattern?

### The Core Insight

```
create_deep_agent() 返回 CompiledStateGraph（Runnable）
                          ↓
              可以直接作为 LangGraph 节点使用
```

### Benefits

| Deep Agent Only     | LangGraph Only          | Hybrid (This Pattern) |
| ------------------- | ----------------------- | --------------------- |
| ✅ Planning         | ✅ Complex topology     | ✅ Both!              |
| ✅ File system      | ✅ Parallel execution   | ✅ Both!              |
| ✅ Sub-agents       | ✅ Conditional routing  | ✅ Both!              |
| ❌ Limited topology | ❌ No built-in planning | ✅ Both!              |

---

## 🎯 State Mapping Explained

Deep Agent expects this format:

```python
{"messages": [{"role": "user", "content": "..."}]}
```

Your main graph might have:

```python
class MainState(TypedDict):
    query: str
    research_result: str
    analysis_result: str
```

### Wrapper Node Pattern

```python
def agent_node(state: MainState) -> dict:
    """Bridge between MainState and Deep Agent."""

    # === INPUT MAPPING ===
    agent_input = {
        "messages": [{"role": "user", "content": state["query"]}]
    }

    # === CALL AGENT ===
    agent_result = my_agent.invoke(agent_input)

    # === OUTPUT MAPPING ===
    # Only extract what you need!
    return {
        "research_result": agent_result["messages"][-1].content
    }
```

### What NOT to Do

```python
# ❌ WRONG: Leaking internal state
def bad_node(state):
    result = agent.invoke(...)
    return result  # Leaks messages, files, todos!

# ✅ CORRECT: Only return what you need
def good_node(state):
    result = agent.invoke(...)
    return {"summary": result["messages"][-1].content}
```

---

## 🔄 Common Patterns

### Pattern 1: Sequential Pipeline

```python
research_agent = create_deep_agent(model, [web_search], "研究专家")
analysis_agent = create_deep_agent(model, [analyze], "分析专家")

def research_node(state):
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"research_result": result["messages"][-1].content}

def analysis_node(state):
    result = analysis_agent.invoke({
        "messages": [{"role": "user", "content": f"分析：{state['research_result']}"}]
    })
    return {"analysis_result": result["messages"][-1].content}

builder = StateGraph(State)
builder.add_node("research", research_node)
builder.add_node("analysis", analysis_node)
builder.add_edge(START, "research")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", END)
```

### Pattern 2: Expert Router

```python
code_agent = create_deep_agent(model, code_tools, "代码专家")
research_agent = create_deep_agent(model, search_tools, "研究专家")

def classify(state) -> Literal["code", "research"]:
    if "代码" in state["query"]:
        return "code"
    return "research"

def code_node(state):
    return {"result": code_agent.invoke(...)["messages"][-1].content}

def research_node(state):
    return {"result": research_agent.invoke(...)["messages"][-1].content}

builder.add_node("code", code_node)
builder.add_node("research", research_node)
builder.add_conditional_edges(START, classify)
```

### Pattern 3: Parallel Execution

```python
import operator
from typing import Annotated

class State(TypedDict):
    topic: str
    results: Annotated[list[str], operator.add]  # Reducer!

tech_agent = create_deep_agent(model, tools, "技术分析")
market_agent = create_deep_agent(model, tools, "市场分析")

def tech_node(state):
    result = tech_agent.invoke({"messages": [{"role": "user", "content": state["topic"]}]})
    return {"results": [f"技术: {result['messages'][-1].content}"]}

def market_node(state):
    result = market_agent.invoke({"messages": [{"role": "user", "content": state["topic"]}]})
    return {"results": [f"市场: {result['messages'][-1].content}"]}

builder.add_edge(START, "tech")
builder.add_edge(START, "market")  # Parallel!
builder.add_edge("tech", "summarize")
builder.add_edge("market", "summarize")
```

---

## 📁 Sharing Files Between Agents

### Option 1: Pass Content Through State

```python
def agent_a_node(state):
    result = agent_a.invoke(...)
    return {
        "a_output": result["messages"][-1].content,
        "a_files": result.get("files", {})
    }

def agent_b_node(state):
    # Include A's files in the prompt
    files_context = "\n".join([
        f"File {k}:\n{v}"
        for k, v in state["a_files"].items()
    ])
    result = agent_b.invoke({
        "messages": [{"role": "user", "content": f"{files_context}\n\nTask: ..."}]
    })
    return {"b_output": result["messages"][-1].content}
```

### Option 2: Shared Backend

```python
from deepagents.backend import FilesystemBackend

shared_backend = FilesystemBackend(root_dir="./workspace")

agent_a = create_deep_agent(model, tools, prompt, backend=shared_backend)
agent_b = create_deep_agent(model, tools, prompt, backend=shared_backend)
# Both agents can now read/write to the same filesystem
```

---

## ⚠️ Anti-Patterns

### ❌ Over-nesting

```python
# BAD: Deep Agent calling another Deep Agent as sub-agent
agent_a = create_deep_agent(
    subagents=[another_deep_agent]  # ❌ Don't nest Deep Agents!
)

# GOOD: Flat structure with LangGraph
builder.add_node("agent_a", agent_a_node)
builder.add_node("agent_b", agent_b_node)  # ✅ Side by side
```

### ❌ Using Deep Agent for Simple Tasks

```python
# BAD: Overkill
email_agent = create_deep_agent(tools=[send_email], prompt="Send emails")

# GOOD: Simple function
def send_email_node(state):
    return send_email(state["to"], state["body"])
```

---

## 🔄 With Streaming

```python
# Stream updates including from Deep Agent internals
for chunk in graph.stream(input, stream_mode="updates", subgraphs=True):
    namespace, data = chunk
    if namespace:
        print(f"From Deep Agent: {data}")
    else:
        print(f"From main graph: {data}")
```

---

## 🔗 Next Steps

**Complex topology patterns:**
→ `02_patterns/complex_topology/README.md`

**Send API for dynamic branching:**
→ `02_patterns/send_api_patterns/README.md`

**Complete hybrid example:**
→ `03_examples/hybrid_multi_agent/README.md`

---

## 💡 Key Takeaways

1. **Deep Agent = Compiled LangGraph** → Can be used as node
2. **State mapping** is key: convert between formats
3. **Don't leak internal state** - only return what you need
4. **Flat structure** over nested Deep Agents
5. **Use for complex sub-tasks**, not simple operations
