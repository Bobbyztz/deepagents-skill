# What is Deep Agents?

> **📋 Prerequisites:** None - Start here!
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 The 30-Second Answer

**Deep Agents** is a library (built on LangGraph) that gives you **pre-built superpowers** for complex agents:

- 📋 **Planning** - Built-in TODO lists
- 📁 **File System** - Virtual filesystem for context management
- 🤖 **Sub-agents** - Spawnable worker agents for isolation
- 💾 **Memory** - Long-term persistence across conversations

Think of it as an **"Agent Toolkit"** rather than a new framework.

### 与 LangGraph 的关系

```
Deep Agents = LangGraph + 预配置的中间件
```

**关键理解**：

- `create_deep_agent()` 返回的是一个**编译好的 LangGraph graph**
- Deep Agent 可以作为 LangGraph 节点使用
- 两者可以无缝组合使用

---

## 🤔 Why Deep Agents Exists

### The Problem: Building Complex Agents is Hard

When building agents for real-world tasks, you constantly face:

```python
❌ Context Overflow
  Agent does 10 web searches → context explodes → $$$

❌ No Planning
  Agent randomly tries tools → no coherent strategy

❌ No Memory
  Every conversation starts from scratch

❌ Reinventing Wheels
  Every project builds its own file system, planning logic, etc.
```

### The Solution: Deep Agents

```python
✅ Built-in Capabilities
  Planning, file system, sub-agents all work out of the box

✅ Context Management
  Large results → automatically saved to files
  Sub-agents → isolated contexts

✅ Proven Patterns
  Based on Claude Code, Deep Research, Manus
```

---

## 🏗️ Architecture: The Three Layers

```
Your Code
   ↓
Deep Agents (Middleware Layer)
   ├─ TodoListMiddleware → write_todos tool
   ├─ FilesystemMiddleware → ls, read_file, write_file, edit_file
   ├─ SubAgentMiddleware → task tool
   └─ SummarizationMiddleware → auto-compress history
   ↓
LangGraph (Execution Engine)
   ├─ State management
   ├─ Tool routing
   └─ Graph execution
```

**Key Insight**: Deep Agents doesn't replace LangGraph—it **simplifies** it by providing high-level abstractions.

**重要发现**: `create_deep_agent()` 返回的是一个 `CompiledStateGraph`（Runnable），可以直接作为 LangGraph 节点使用！

---

## ✅ When to Use Deep Agents

### Use Deep Agents When:

✅ **Complex, multi-step tasks**

- Example: "Research quantum computing and write a 2000-word report with citations"
- Needs: Planning, web search, context management

✅ **Large context management**

- Example: Processing 10+ web pages per task
- Needs: File system to offload results

✅ **Specialized subtasks**

- Example: Main agent delegates "data analysis" to a specialized sub-agent
- Needs: Context isolation via sub-agents

✅ **Cross-conversation memory**

- Example: "Remember my preferences" across sessions
- Needs: Long-term memory backed by LangGraph Store

---

### ❌ Don't Use Deep Agents When:

❌ **Simple, single-turn tasks**

- Example: "Translate this text to Spanish"
- Better: Use `create_agent` from LangChain

❌ **Full control over graph flow**

- Example: Custom state machine with 10+ nodes and complex routing
- Better: Build directly with LangGraph (or use hybrid approach)

❌ **Minimal tool usage**

- Example: Pure LLM reasoning without external tools
- Better: Direct LLM API call

---

## 🔍 Deep Agents vs LangGraph vs Hybrid

| Feature                 | Deep Agents | LangGraph Graph API | Hybrid (推荐) |
| ----------------------- | ----------- | ------------------- | ------------- |
| **Setup Complexity**    | Low         | Medium              | Medium        |
| **Planning Built-in**   | ✅          | ❌                  | ✅            |
| **File System**         | ✅          | Manual              | ✅            |
| **Sub-agents**          | ✅          | Manual              | ✅            |
| **Custom Flow Control** | Limited     | ✅                  | ✅            |
| **Complex Topology**    | ❌          | ✅                  | ✅            |
| **Multi-step Tasks**    | ✅          | ✅                  | ✅            |

**Rule of Thumb:**

- Simple task → `create_agent`
- Complex task, don't want to configure everything → **Deep Agents**
- Complex task, need full control → **LangGraph**
- Complex task, need both flexibility and built-in features → **Hybrid (Deep Agent as LangGraph node)**

---

## 🧩 Core Concepts

### 1. Middleware Architecture

Deep Agents uses **composable middleware** to add capabilities:

```python
agent = create_deep_agent(
    tools=[my_tool],
    # These middleware are automatically added:
    # - TodoListMiddleware
    # - FilesystemMiddleware
    # - SubAgentMiddleware
    # - SummarizationMiddleware
)
```

Each middleware:

- Provides tools (e.g., `write_todos`, `task`)
- Injects instructions into the system prompt
- Can be configured or replaced

### 2. Built-in Tools

Without writing any code, your agent gets:

| Tool                                            | Purpose                  | Example                               |
| ----------------------------------------------- | ------------------------ | ------------------------------------- |
| `write_todos`                                   | Create/update task lists | Plan research into 5 steps            |
| `ls` / `read_file` / `write_file` / `edit_file` | File operations          | Save search results to `/research.md` |
| `glob` / `grep`                                 | File search              | Find all `.py` files with "TODO"      |
| `task`                                          | Spawn sub-agent          | Delegate "analyze data" to specialist |

### 3. Context Isolation via Sub-agents

**Problem**: If the main agent does 20 web searches, its context becomes huge.

**Solution**:

```
Main Agent (clean context, 10 messages)
  ↓ task() call
Sub-agent (messy context, 50 messages: searches, reflections...)
  ↓ returns summary
Main Agent (still clean, 12 messages)
```

### 4. File System as Communication

Files are not just storage—they're how components communicate:

```python
# Agent workflow:
1. write_file("/user_request.md", original_query)
2. sub-agent does research → writes findings to files
3. write_file("/final_report.md", synthesized_report)
4. read_file("/user_request.md") to verify coverage
```

### 5. Deep Agent as LangGraph Node【核心新概念】

Deep Agent 可以嵌入到更大的 LangGraph 工作流中：

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent

# 创建 Deep Agent
research_agent = create_deep_agent(model, tools, system_prompt)

# 作为 LangGraph 节点使用
def research_node(state):
    result = research_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"research_result": result["messages"][-1].content}

builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_edge(START, "research")
builder.add_edge("research", END)
graph = builder.compile()
```

详见: `deep_agent_as_node.md`

---

## 📊 Real-World Example: Deep Research

The `deep_research` example (included in this repository) shows Deep Agents in action:

**User**: "Compare Python vs JavaScript for web development"

**Agent**:

1. **Plans** (write_todos): Break into sub-tasks
2. **Delegates** (task): Spawn 2 parallel sub-agents
   - Sub-agent 1: Research Python
   - Sub-agent 2: Research JavaScript
3. **Synthesizes**: Merge findings, consolidate citations
4. **Writes Report**: `/final_report.md` with citations
5. **Verifies**: Reads `/user_request.md` to confirm completeness

**Result**: Professional research report with inline citations `[1], [2], [3]`

→ Deep dive: `03_examples/deep_research/00_overview.md`

---

## 🚀 Quick Decision Tree

```
Do you need...

┌─ Simple Q&A? → Use create_agent()
│
├─ Multi-step task with planning? → Use Deep Agents
│
├─ Custom state machine with complex topology? → Use LangGraph directly
│
├─ Complex topology + planning/file system? → Use Hybrid (Deep Agent as node)
│
└─ Not sure? → Start with Deep Agents (easiest to upgrade to hybrid)
```

---

## 🔗 What's Next?

Now that you understand **what** Deep Agents is and **when** to use it:

**Ready to build?**
→ `minimal_example.md` - 15 lines of code to your first agent

**Want to compare with LangGraph?**
→ `architecture_comparison.md` - Detailed comparison of three approaches

**Want to learn hybrid architecture?**
→ `deep_agent_as_node.md` - 【核心】Deep Agent 作为 LangGraph 节点

**Want to see a complete example?**
→ `03_examples/deep_research/00_overview.md` - Full project walkthrough

---

## 📚 Knowledge Sources

This V2 knowledge base integrates and self-contains:

- Deep Agents official documentation
- LangGraph core concepts (Graph API, Functional API, Persistence, Streaming, Memory)
- Production best practices

**Note**: All LangGraph knowledge has been extracted and integrated into `04_langgraph_integration/`. No external documentation dependencies required.
