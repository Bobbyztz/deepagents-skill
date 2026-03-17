# Migration Guide

> **📋 Prerequisites:**
>
> - `00_quickstart/architecture_comparison.md`
> - `00_quickstart/deep_agent_as_node.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

Migration paths covered:

- Pure LLM → LangGraph
- LangChain Agent → LangGraph
- Deep Agents V1 → V2 (with LangGraph)
- Pure LangGraph ↔ Deep Agents

---

## 📖 Path 1: Pure LLM → LangGraph

### Before: Simple LLM Call

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5-20250929")

def chat(message: str) -> str:
    response = model.invoke([{"role": "user", "content": message}])
    return response.content
```

### After: LangGraph with Persistence

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

def agent_node(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

graph = builder.compile(checkpointer=MemorySaver())

# Now has memory!
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"messages": [HumanMessage("Hi")]}, config)
```

**Benefits gained:**

- ✅ Conversation memory
- ✅ State persistence
- ✅ Debugging (state inspection)

---

## 📖 Path 2: LangChain Agent → LangGraph

### Before: LangChain create_react_agent

```python
from langchain.agents import create_react_agent, AgentExecutor

agent = create_react_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "Calculate 5 * 7"})
```

### After: LangGraph ReAct

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def agent_node(state: MessagesState):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: MessagesState):
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    return {"messages": results}

def should_continue(state) -> Literal["tools", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()
```

**Benefits gained:**

- ✅ Full control over flow
- ✅ Persistence support
- ✅ Streaming support
- ✅ Human-in-the-loop capability

---

## 📖 Path 3: Deep Agents V1 → V2

### V1 Code (No LangGraph Integration)

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,
    tools=[web_search],
    system_prompt="Research assistant",
    subagents=[research_subagent]
)

result = agent.invoke({"messages": [{"role": "user", "content": query}]})
```

### V2 Code Option A: Keep Pure Deep Agents

```python
# Mostly the same! V2 is backward compatible
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    model=model,
    tools=[web_search],
    system_prompt="Research assistant",
    subagents=[research_subagent],
    checkpointer=MemorySaver()  # NEW: Add persistence
)

# Now with memory
config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke({"messages": [...]}, config)
```

### V2 Code Option B: Hybrid Architecture (Recommended)

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent

# Keep your Deep Agent
research_agent = create_deep_agent(
    model=model,
    tools=[web_search],
    system_prompt="Research specialist"
)

# Wrap as LangGraph node
def research_node(state):
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"research": result["messages"][-1].content}

# Add to LangGraph for complex orchestration
builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_node("analyze", analyze_node)  # Another Deep Agent or regular node
builder.add_edge(START, "research")
builder.add_edge("research", "analyze")
builder.add_edge("analyze", END)

graph = builder.compile()
```

**When to use Hybrid:**

- Multiple stages with different agents
- Complex routing logic
- Parallel execution needed
- Need LangGraph features (Send API, etc.)

---

## 📖 Path 4: Pure LangGraph → Adding Deep Agent

### Before: All Manual

```python
def complex_research_node(state):
    # 50+ lines of:
    # - Planning logic
    # - Tool calls
    # - File management
    # - Iteration
    ...
```

### After: Use Deep Agent for Complex Tasks

```python
from deepagents import create_deep_agent

# Replace complex manual node with Deep Agent
research_agent = create_deep_agent(
    model=model,
    tools=[web_search, think_tool],
    system_prompt="""You are a research specialist.
    1. Plan your research
    2. Search systematically
    3. Reflect after each search
    4. Return comprehensive findings
    """
)

def research_node(state):
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"research": result["messages"][-1].content}
```

**Benefits:**

- ✅ Built-in planning
- ✅ Built-in file system
- ✅ Built-in sub-agents
- ✅ Less code to maintain

---

## 🔄 Quick Migration Checklist

### From Pure LLM

- [ ] Define State (TypedDict)
- [ ] Create agent node
- [ ] Add checkpointer for memory
- [ ] Update invocation to use config with thread_id

### From LangChain Agent

- [ ] Convert to StateGraph
- [ ] Create agent and tool nodes
- [ ] Add conditional routing
- [ ] Add checkpointer
- [ ] Update streaming if used

### From Deep Agents V1

- [ ] Add checkpointer if needed
- [ ] Consider hybrid architecture for complex cases
- [ ] Update imports if any changed
- [ ] Test sub-agent behavior

### To Hybrid Architecture

- [ ] Identify complex sub-tasks
- [ ] Create specialized Deep Agents
- [ ] Wrap as LangGraph nodes
- [ ] Build orchestration graph
- [ ] Test state mapping

---

## ⚠️ Common Migration Issues

### State Mismatch

```python
# ❌ Wrong: Deep Agent state leaking
def node(state):
    result = agent.invoke(...)
    return result  # Includes messages, files, todos

# ✅ Correct: Extract only needed fields
def node(state):
    result = agent.invoke(...)
    return {"summary": result["messages"][-1].content}
```

### Missing Config

```python
# ❌ Wrong: No thread_id
result = graph.invoke(input)

# ✅ Correct: Include thread_id for persistence
result = graph.invoke(input, {"configurable": {"thread_id": "123"}})
```

### Reducer Issues

```python
# ❌ Wrong: Parallel results overwrite
class State(TypedDict):
    result: str

# ✅ Correct: Use reducer for parallel
class State(TypedDict):
    results: Annotated[list[str], operator.add]
```

---

## 🔗 Next Steps

**Architecture comparison:**
→ `00_quickstart/architecture_comparison.md`

**Deep Agent as node:**
→ `00_quickstart/deep_agent_as_node.md`

**Production guide:**
→ `06_production_guide.md`

---

## 💡 Key Takeaways

1. **V2 is backward compatible** with V1 Deep Agents
2. **Hybrid architecture** is recommended for complex systems
3. **State mapping** is key when mixing approaches
4. **Checkpointer** should be added for production use
