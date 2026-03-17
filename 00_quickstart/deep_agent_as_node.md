# Deep Agent 作为 LangGraph 节点使用指南【核心】

> **📋 Prerequisites:**
>
> - `what_is_deep_agents.md`
> - `langgraph_quickstart.md`（推荐）
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from typing import TypedDict

# 1. 创建 Deep Agent（它本身就是编译好的 LangGraph graph）
research_agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-5-20250929"),
    tools=[web_search, think_tool],
    system_prompt="你是研究专家"
)

# 2. 定义主图状态
class MainState(TypedDict):
    query: str
    research_result: str

# 3. 创建包装节点（状态映射）
def research_node(state: MainState):
    # 输入映射：MainState → Deep Agent 的 messages 格式
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    # 输出映射：Deep Agent 的输出 → MainState
    return {"research_result": result["messages"][-1].content}

# 4. 构建主图
builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_edge(START, "research")
builder.add_edge("research", END)
graph = builder.compile()

# 5. 使用
result = graph.invoke({"query": "量子计算的最新进展"})
print(result["research_result"])
```

---

## 📖 Why This Works

### 核心原理

**`create_deep_agent()` 返回的是一个编译好的 LangGraph graph**

```python
agent = create_deep_agent(...)
# agent 是一个 CompiledStateGraph（Runnable）
```

**证据**（来自官方文档）：

> **Result**: `agent` is a runnable LangGraph compiled graph.

**这意味着**：

- ✅ Deep Agent 本质上就是 LangGraph graph
- ✅ 已经编译（compiled），可以直接调用
- ✅ 是 Runnable 接口，符合 LangChain/LangGraph 标准
- ✅ 可以作为另一个 LangGraph 的节点

---

## 🏗️ 层次架构

```
Layer 1: LangGraph 主图（超级编排器）
├── 负责高层拓扑
├── 条件路由、并行执行
└── 状态协调
    ↓
Layer 2: Deep Agent 节点（中层编排器）
├── 处理复杂子任务
├── 内置 planning、file system
└── 管理自己的 sub-agents
    ↓
Layer 3: Sub-agents（工作器）
├── 执行具体操作
└── 上下文隔离
```

**最佳实践**：

- 主图处理**高层逻辑**（什么时候做什么）
- Deep Agent 处理**复杂子任务**（如何做）

---

## 🎯 三种使用方式

### 方式 1：作为子图节点（顺序执行）

**场景**：多阶段流水线，每阶段是独立复杂任务

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent
from typing import TypedDict

class ResearchState(TypedDict):
    user_query: str
    literature_review: str | None
    experiment_design: str | None
    final_paper: str | None

# 创建专业 Deep Agents
literature_agent = create_deep_agent(
    model=model,
    tools=[academic_search, think_tool],
    system_prompt="你是文献研究专家"
)

experiment_agent = create_deep_agent(
    model=model,
    tools=[design_tool],
    system_prompt="你是实验设计专家"
)

writing_agent = create_deep_agent(
    model=model,
    tools=[grammar_check],
    system_prompt="你是学术写作专家"
)

# 包装节点
def literature_node(state: ResearchState):
    result = literature_agent.invoke({
        "messages": [{"role": "user", "content": state["user_query"]}]
    })
    return {"literature_review": result["messages"][-1].content}

def experiment_node(state: ResearchState):
    result = experiment_agent.invoke({
        "messages": [{"role": "user", "content": f"基于文献设计实验：\n{state['literature_review']}"}]
    })
    return {"experiment_design": result["messages"][-1].content}

def writing_node(state: ResearchState):
    result = writing_agent.invoke({
        "messages": [{"role": "user", "content": f"撰写论文，整合：\n{state['literature_review']}\n{state['experiment_design']}"}]
    })
    return {"final_paper": result["messages"][-1].content}

# 构建流水线
builder = StateGraph(ResearchState)
builder.add_node("literature", literature_node)
builder.add_node("experiment", experiment_node)
builder.add_node("writing", writing_node)

builder.add_edge(START, "literature")
builder.add_edge("literature", "experiment")
builder.add_edge("experiment", "writing")
builder.add_edge("writing", END)

graph = builder.compile()
```

**流程**：

```
用户查询 → 文献研究 → 实验设计 → 论文写作 → 完成
```

---

### 方式 2：条件路由到不同 Deep Agent

**场景**：专家路由系统，根据输入选择专家

```python
from typing import Literal

class ExpertState(TypedDict):
    query: str
    category: str
    result: str

# 创建专家 Deep Agents
code_agent = create_deep_agent(model, [code_tools], "你是代码专家")
research_agent = create_deep_agent(model, [search_tools], "你是研究专家")
writing_agent = create_deep_agent(model, [writing_tools], "你是写作专家")

# 分类节点
def classify_node(state: ExpertState):
    # 简单分类逻辑（也可以用 LLM）
    query = state["query"].lower()
    if "代码" in query or "编程" in query:
        return {"category": "code"}
    elif "研究" in query or "分析" in query:
        return {"category": "research"}
    else:
        return {"category": "writing"}

# 专家节点
def code_node(state: ExpertState):
    result = code_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"result": result["messages"][-1].content}

def research_node(state: ExpertState):
    result = research_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"result": result["messages"][-1].content}

def writing_node(state: ExpertState):
    result = writing_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"result": result["messages"][-1].content}

# 路由函数
def route_to_expert(state: ExpertState) -> Literal["code", "research", "writing"]:
    return state["category"]

# 构建图
builder = StateGraph(ExpertState)
builder.add_node("classify", classify_node)
builder.add_node("code", code_node)
builder.add_node("research", research_node)
builder.add_node("writing", writing_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_to_expert)
builder.add_edge("code", END)
builder.add_edge("research", END)
builder.add_edge("writing", END)

graph = builder.compile()
```

**流程**：

```
查询 → 分类 → 代码专家
            → 研究专家
            → 写作专家
```

---

### 方式 3：并行执行多个 Deep Agent

**场景**：多维度分析，并行执行后汇总

```python
import operator
from typing import Annotated

class ParallelState(TypedDict):
    topic: str
    results: Annotated[list[str], operator.add]  # reducer: 自动合并
    final_summary: str

# 创建多个研究 Deep Agents
tech_agent = create_deep_agent(model, tools, "你负责技术方面研究")
market_agent = create_deep_agent(model, tools, "你负责市场方面研究")
impact_agent = create_deep_agent(model, tools, "你负责社会影响研究")

def tech_node(state: ParallelState):
    result = tech_agent.invoke({"messages": [{"role": "user", "content": f"技术分析：{state['topic']}"}]})
    return {"results": [f"技术：{result['messages'][-1].content}"]}

def market_node(state: ParallelState):
    result = market_agent.invoke({"messages": [{"role": "user", "content": f"市场分析：{state['topic']}"}]})
    return {"results": [f"市场：{result['messages'][-1].content}"]}

def impact_node(state: ParallelState):
    result = impact_agent.invoke({"messages": [{"role": "user", "content": f"影响分析：{state['topic']}"}]})
    return {"results": [f"影响：{result['messages'][-1].content}"]}

def summarize_node(state: ParallelState):
    combined = "\n\n".join(state["results"])
    return {"final_summary": f"综合分析：\n{combined}"}

# 构建并行图
builder = StateGraph(ParallelState)
builder.add_node("tech", tech_node)
builder.add_node("market", market_node)
builder.add_node("impact", impact_node)
builder.add_node("summarize", summarize_node)

# 并行扇出
builder.add_edge(START, "tech")
builder.add_edge(START, "market")
builder.add_edge(START, "impact")

# 扇入汇总
builder.add_edge("tech", "summarize")
builder.add_edge("market", "summarize")
builder.add_edge("impact", "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()
```

**流程**：

```
       ┌→ 技术分析 ─┐
主题 ──┼→ 市场分析 ─┼→ 汇总 → 完成
       └→ 影响分析 ─┘
```

---

## 🔧 状态映射机制

### 关键：输入/输出转换

Deep Agent 的状态格式：

```python
{
    "messages": [...],
    "files": {...},
    "todos": [...]
}
```

主图状态可能不同：

```python
class MainState(TypedDict):
    query: str
    research_result: str
    analysis_result: str
```

**桥接函数模式**：

```python
def bridge_to_deep_agent(main_state: MainState) -> dict:
    """主图状态 → Deep Agent 输入"""
    return {
        "messages": [
            {"role": "user", "content": main_state["query"]}
        ]
    }

def bridge_from_deep_agent(deep_result: dict, main_state: MainState) -> dict:
    """Deep Agent 输出 → 主图状态更新"""
    return {
        "research_result": deep_result["messages"][-1].content,
        # 可选：保存生成的文件
        # "files": deep_result.get("files", {})
    }

def deep_agent_node(state: MainState):
    agent_input = bridge_to_deep_agent(state)
    result = my_deep_agent.invoke(agent_input)
    return bridge_from_deep_agent(result, state)
```

---

## ⚠️ Anti-Patterns 警告

### ❌ Anti-Pattern 1: 过度嵌套

```python
# ❌ 错误：3层以上的 Deep Agent 嵌套
main_agent → sub_agent_1 → sub_sub_agent → sub_sub_sub_agent

# ✅ 正确：使用 LangGraph 主图 + 扁平化 Deep Agent 节点
main_graph
├── deep_agent_1 (node)
├── deep_agent_2 (node)
└── deep_agent_3 (node)
```

### ❌ Anti-Pattern 2: 状态污染

```python
# ❌ 错误：直接传递 Deep Agent 内部状态
def node(state):
    result = agent.invoke(...)
    return result  # 泄露 messages、files、todos

# ✅ 正确：只提取需要的字段
def node(state):
    result = agent.invoke(...)
    return {"summary": result["messages"][-1].content}
```

### ❌ Anti-Pattern 3: 文件系统冲突

```python
# ❌ 错误：并行 Deep Agent 写同一文件
agent_a → /output/result.txt
agent_b → /output/result.txt  # 冲突！

# ✅ 正确：命名空间隔离
agent_a → /workspace/agent_a/result.txt
agent_b → /workspace/agent_b/result.txt
```

### ❌ Anti-Pattern 4: 滥用 Deep Agent

```python
# ❌ 错误：简单任务用 Deep Agent
email_sender = create_deep_agent(tools=[send_email], system_prompt="发邮件")

# ✅ 正确：简单任务用普通函数
def send_email_node(state):
    return send_email(state["recipient"], state["body"])
```

---

## 📁 文件系统共享

**问题**：多个 Deep Agent 需要共享文件？

**方案 1**：通过状态传递文件内容

```python
def agent_a_node(state):
    result = agent_a.invoke(...)
    return {
        "a_output": result["messages"][-1].content,
        "shared_files": result.get("files", {})
    }

def agent_b_node(state):
    # 将 A 的文件内容注入到 B 的输入
    files_context = "\n".join([f"{k}:\n{v}" for k, v in state["shared_files"].items()])
    result = agent_b.invoke({
        "messages": [{"role": "user", "content": f"参考文件：\n{files_context}\n\n任务：..."}]
    })
    return {"b_output": result["messages"][-1].content}
```

**方案 2**：使用共享 Backend

```python
from deepagents.backend import FilesystemBackend

shared_backend = FilesystemBackend(root_dir="./shared_workspace")

agent_1 = create_deep_agent(model, tools, prompt, backend=shared_backend)
agent_2 = create_deep_agent(model, tools, prompt, backend=shared_backend)
# 现在两个 agent 共享文件系统
```

---

## 🎯 决策框架

```
何时使用单个 Deep Agent？
├─ 单一复杂任务
├─ 不需要跨 Agent 编排
└─ 内置功能足够

何时使用 Deep Agent 作为节点？
├─ 多阶段流水线
├─ 专家路由系统
├─ 需要并行执行
└─ 需要复杂拓扑 + 内置功能
```

---

## 🔗 Next Steps

**学习复杂拓扑模式**：
→ `02_patterns/complex_topology/README.md`

**学习 Send API 动态分支**：
→ `02_patterns/send_api_patterns/README.md`

**查看完整示例**：
→ `03_examples/hybrid_multi_agent/README.md`

**原子操作详解**：
→ `01_atomic/11_use_deep_agent_as_node.md`

---

## 📊 对比总结

| 方案               | 适用场景     | 优势         | 注意事项     |
| ------------------ | ------------ | ------------ | ------------ |
| **顺序节点**       | 多阶段流水线 | 清晰、易维护 | 顺序执行     |
| **条件路由**       | 专家选择     | 灵活路由     | 分类逻辑设计 |
| **并行执行**       | 多维度分析   | 快速、全面   | 结果汇总     |
| **纯 Deep Agents** | 单一任务     | 最简单       | 拓扑受限     |
| **纯 LangGraph**   | 自定义拓扑   | 完全控制     | 需自建功能   |

**核心结论**：

> **组合优于单一** - LangGraph 主图（编排） + Deep Agent 节点（执行） = 最佳实践
