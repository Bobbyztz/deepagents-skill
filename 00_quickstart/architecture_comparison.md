# Architecture Comparison: Deep Agents vs LangGraph vs Hybrid

> **📋 Prerequisites:**
>
> - `what_is_deep_agents.md` (recommended)
> - `langgraph_quickstart.md` (recommended)
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer: Which Should I Use?

```
你的任务复杂度？
├─ 简单单步 → 直接 LLM API 调用
├─ 中等复杂（研究、写作） → Deep Agents
├─ 复杂拓扑（多分支、并行） → LangGraph Graph API
└─ 复杂拓扑 + 需要planning/文件系统 → Hybrid【推荐】
```

---

## 📊 Three Approaches Overview

| 方面            | Deep Agents           | LangGraph Graph API       | LangGraph Functional API |
| --------------- | --------------------- | ------------------------- | ------------------------ |
| **入口点**      | `create_deep_agent()` | `StateGraph().compile()`  | `@entrypoint()`          |
| **代码量**      | ~15 行                | ~50 行                    | ~30 行                   |
| **学习曲线**    | 低                    | 中                        | 低-中                    |
| **状态管理**    | 自动                  | 显式 TypedDict            | 函数参数                 |
| **条件路由**    | 内置（prompt）        | `add_conditional_edges()` | `if/else`                |
| **并行执行**    | 通过 sub-agents       | 多入口边                  | 手动                     |
| **Planning**    | ✅ 内置               | ❌ 需自建                 | ❌ 需自建                |
| **File System** | ✅ 内置               | ❌ 需自建                 | ❌ 需自建                |
| **Sub-agents**  | ✅ 内置               | ❌ 需自建                 | ❌ 需自建                |
| **复杂拓扑**    | ❌ 有限               | ✅ 完全支持               | ✅ 支持                  |
| **可视化**      | ✅                    | ✅ Studio                 | ✅ Studio                |
| **Persistence** | ✅                    | ✅ Checkpointer           | ✅ Checkpointer          |
| **Streaming**   | ✅                    | ✅ 5 种模式               | ✅                       |

---

## 📖 Detailed Comparison

### 1. Deep Agents

**最适合**：研究类任务、需要 planning 和文件系统的场景

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5-20250929")

agent = create_deep_agent(
    model=model,
    tools=[web_search],
    system_prompt="你是研究专家"
)

result = agent.invoke({"messages": [{"role": "user", "content": "研究量子计算"}]})
```

**优点**：

- ✅ 开箱即用的 planning、file system、sub-agents
- ✅ 上下文隔离自动管理
- ✅ 最少代码量

**缺点**：

- ❌ 复杂拓扑支持有限
- ❌ 自定义流程控制受限
- ❌ 只支持"一父多子"结构

---

### 2. LangGraph Graph API

**最适合**：复杂工作流、需要可视化、团队协作

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]
    research_result: str

def research_node(state):
    # 执行研究
    return {"research_result": "..."}

def analysis_node(state):
    # 基于研究结果分析
    return {"messages": ["分析完成"]}

builder = StateGraph(State)
builder.add_node("research", research_node)
builder.add_node("analysis", analysis_node)
builder.add_edge(START, "research")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", END)

graph = builder.compile()
```

**优点**：

- ✅ 完全控制工作流拓扑
- ✅ 支持并行、条件分支、循环
- ✅ 可视化调试
- ✅ 团队协作友好

**缺点**：

- ❌ 更多样板代码
- ❌ 需要手动实现 planning、file system
- ❌ 学习曲线较陡

---

### 3. LangGraph Functional API

**最适合**：线性工作流、快速原型、现有代码改造

```python
from langgraph.func import entrypoint, task

@task
def research(query: str):
    # 执行研究
    return {"result": "..."}

@task
def analyze(data: dict):
    # 分析数据
    return {"analysis": "..."}

@entrypoint()
def workflow(query: str):
    research_result = research(query).result()
    analysis_result = analyze(research_result).result()
    return analysis_result
```

**优点**：

- ✅ 最小样板代码
- ✅ 标准 Python 控制流
- ✅ 易于集成现有代码

**缺点**：

- ❌ 复杂拓扑需要手动实现
- ❌ 可视化支持有限
- ❌ 需要手动实现 planning 等

---

### 4. Hybrid: Deep Agent as LangGraph Node【推荐】

**最适合**：复杂拓扑 + 需要 Deep Agents 内置功能

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# 创建专业 Deep Agents
research_agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-5-20250929"),
    tools=[web_search, think_tool],
    system_prompt="你是研究专家"
)

analysis_agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-5-20250929"),
    tools=[analyze_data],
    system_prompt="你是分析专家"
)

# 包装为 LangGraph 节点
def research_node(state):
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"research_result": result["messages"][-1].content}

def analysis_node(state):
    result = analysis_agent.invoke({
        "messages": [{"role": "user", "content": state["research_result"]}]
    })
    return {"final_output": result["messages"][-1].content}

# 用 LangGraph 编排
builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_node("analysis", analysis_node)
builder.add_edge(START, "research")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", END)

graph = builder.compile()
```

**优点**：

- ✅ LangGraph 的拓扑灵活性
- ✅ Deep Agents 的内置功能
- ✅ 每个节点独立的上下文管理
- ✅ 最佳实践组合

**缺点**：

- ⚠️ 需要理解两个系统
- ⚠️ 状态映射需要注意

→ 详见 `deep_agent_as_node.md`

---

## 🎯 Decision Framework

### 问题 1: 任务复杂度？

```
简单（1-2 步骤）
  → 直接 LLM API 或 create_agent()

中等（3-5 步骤，单一领域）
  → Deep Agents

复杂（多领域、多阶段、需要并行）
  → LangGraph 或 Hybrid
```

### 问题 2: 需要内置功能？

```
需要 Planning?
  ├─ 是 → Deep Agents 或 Hybrid
  └─ 否 → 继续判断

需要 File System?
  ├─ 是 → Deep Agents 或 Hybrid
  └─ 否 → 继续判断

需要 Sub-agents 上下文隔离?
  ├─ 是 → Deep Agents 或 Hybrid
  └─ 否 → LangGraph
```

### 问题 3: 拓扑复杂度？

```
线性流程（A → B → C）
  → 都可以，Deep Agents 最简单

条件分支（A → B 或 C）
  → LangGraph Graph API 或 Hybrid

并行扇出（A → [B, C, D] → E）
  → LangGraph Graph API 或 Hybrid

动态分支（运行时决定并行数量）
  → LangGraph Send API
```

### 问题 4: 团队协作？

```
单人开发
  → 选择最适合任务的方案

团队协作
  → LangGraph Graph API（可视化、模块化）
```

---

## 📊 Use Case Matrix

| 场景           | 推荐方案                      | 原因                            |
| -------------- | ----------------------------- | ------------------------------- |
| 简单聊天机器人 | LangGraph Graph API           | 简单拓扑，不需要 planning       |
| 研究报告生成   | Deep Agents                   | 需要 planning、file system      |
| 多步骤审批流程 | LangGraph Graph API           | 复杂条件分支                    |
| 并行数据处理   | LangGraph + Send API          | 动态并行                        |
| 多专家协作系统 | **Hybrid**                    | 复杂拓扑 + 每个专家需要独立功能 |
| 快速原型       | Deep Agents 或 Functional API | 最少代码                        |
| 生产系统       | **Hybrid**                    | 灵活性 + 可维护性               |

---

## 💡 Migration Paths

### From Deep Agents to Hybrid

```python
# Before: 单一 Deep Agent
agent = create_deep_agent(model, tools, system_prompt)
result = agent.invoke(input)

# After: Deep Agent as node in LangGraph
def agent_node(state):
    result = agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"output": result["messages"][-1].content}

builder = StateGraph(State)
builder.add_node("agent", agent_node)
# ... add more nodes, edges
```

### From LangGraph to Hybrid

```python
# Before: 手动实现的复杂节点
def complex_node(state):
    # 100+ lines of planning, tool calls, context management
    ...

# After: 用 Deep Agent 替代
complex_agent = create_deep_agent(model, tools, system_prompt)

def complex_node(state):
    result = complex_agent.invoke(...)
    return {"output": result["messages"][-1].content}
```

---

## 🔗 Next Steps

**Ready to use Deep Agents?**
→ `minimal_example.md`

**Ready to use LangGraph?**
→ `langgraph_quickstart.md`

**Ready for Hybrid?**
→ `deep_agent_as_node.md` 【核心】

**Want complete examples?**
→ `03_examples/` 目录

---

## 📚 Summary

| 如果你...            | 使用...                         |
| -------------------- | ------------------------------- |
| 想快速开始研究类任务 | Deep Agents                     |
| 需要复杂工作流控制   | LangGraph Graph API             |
| 想最小化代码改动     | LangGraph Functional API        |
| 需要两者优势         | **Hybrid (Deep Agent as Node)** |
