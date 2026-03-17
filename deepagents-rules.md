# Deep Agents V2 Project Rules

> **LangGraph 版本要求**: `>=0.2.0`

## Knowledge Base Location

`deepagents_skills_v2/` - AI-optimized skills library for Deep Agents + LangGraph integration

## 核心理念

V2 知识库实现 **LangGraph 特性与 Deep Agents 架构的深度整合**，提供三种实现路径：

1. **Deep Agents 路径**：使用 `create_deep_agent()` API（快速搭建）
2. **LangGraph Graph API 路径**：使用 `StateGraph`（复杂拓扑）
3. **LangGraph Functional API 路径**：使用 `@entrypoint`、`@task`（最小样板）

## Usage Protocol

### 1. Always Start Here

- First read: [deepagents_skills_v2/ROUTER.md]
- It contains a decision tree to locate the exact file you need

### 2. Architecture Selection Decision Tree

```
我的任务复杂度如何？
├─ 简单单步任务 → 不需要 Agent
├─ 中等复杂度（3-5 步骤，单一领域）
│   └─ 一个 Deep Agent → 00_quickstart/templates/basic_agent/
├─ 高复杂度（多领域、多阶段）
│   └─ 继续决策 ↓
│
任务是否有明确的"阶段划分"？
├─ 有（如：研究 → 分析 → 写作）
│   └─ LangGraph 主图 + Deep Agent 节点
│   └─ 参考: 00_quickstart/deep_agent_as_node.md
├─ 没有（复杂但单一连贯任务）
│   └─ 一个 Deep Agent + 多 sub-agents
│   └─ 参考: 01_atomic/03_configure_subagent.md
│
需要什么高级特性？
├─ 持久化状态 → 04_langgraph_integration/03_persistence_guide.md
├─ 流式输出 → 04_langgraph_integration/05_streaming_guide.md
├─ 人机交互 → 02_patterns/human_in_loop/
├─ 复杂拓扑（并行、条件） → 02_patterns/complex_topology/
└─ 动态分支 → 02_patterns/send_api_patterns/
```

### 3. Task-based Routing

**Creating a new agent:**

| 场景               | 推荐路径                | 文件                                       |
| ------------------ | ----------------------- | ------------------------------------------ |
| 最简单的 Agent     | Deep Agents             | `00_quickstart/templates/basic_agent/`     |
| 研究类 Agent       | Deep Agents             | `00_quickstart/templates/research_agent/`  |
| 纯 LangGraph Agent | Graph API               | `00_quickstart/templates/langgraph_basic/` |
| 混合架构 Agent     | Deep Agents + LangGraph | `00_quickstart/templates/hybrid_agent/`    |

**Adding features to existing agent:**

| Feature          | Deep Agents 方式                       | LangGraph 方式                                     |
| ---------------- | -------------------------------------- | -------------------------------------------------- |
| Custom tool      | `01_atomic/02_add_tool.md`             | 同文件                                             |
| Sub-agent        | `01_atomic/03_configure_subagent.md`   | `01_Capabilities/06_Subgraphs.md`                  |
| File system      | `01_atomic/04_setup_filesystem.md`     | N/A                                                |
| Planning         | `01_atomic/05_enable_planning.md`      | N/A                                                |
| Human-in-loop    | `01_atomic/06_add_human_in_loop.md`    | `02_patterns/human_in_loop/`                       |
| Long-term memory | `01_atomic/07_add_long_term_memory.md` | `04_langgraph_integration/04_memory_guide.md`      |
| Persistence      | `01_atomic/08_add_persistence.md`      | `04_langgraph_integration/03_persistence_guide.md` |
| Streaming        | `01_atomic/09_add_streaming.md`        | `04_langgraph_integration/05_streaming_guide.md`   |

### 4. Code Extraction Rules

- Every skill file has "⚡ Quick Answer" section with ready-to-use code
- Copy Quick Answer code directly - it's tested and complete
- Check "📋 Prerequisites" before reading a file
- Follow "🔗 Next Steps" for related content
- **代码需标注 LangGraph 版本要求**（`>=0.2.0`）

### 5. Progressive Loading

- **Don't** read the entire knowledge base at once
- **Do** follow the routing path and read only relevant files
- **Do** check Prerequisites and load them first if needed

### 6. Design Patterns Priority

When building production agents:

1. Use context isolation (sub-agents) for complex multi-step tasks
2. Add reflection loop (think_tool) for quality-driven search
3. Define explicit workflows in system prompts
4. Parallelize only for explicit comparisons
5. **考虑使用 LangGraph 主图 + Deep Agent 节点的混合架构**
6. ALWAYS read and understand relevant files before proposing edits

## 三种架构对比

| 特性         | Deep Agents                    | LangGraph Graph API       | LangGraph Functional API |
| ------------ | ------------------------------ | ------------------------- | ------------------------ |
| **入口点**   | `create_deep_agent()`          | `StateGraph().compile()`  | `@entrypoint()`          |
| **状态管理** | 自动（messages, files, todos） | 显式 TypedDict            | 函数参数                 |
| **条件路由** | 内置（通过 prompt）            | `add_conditional_edges()` | `if/else` 语句           |
| **并行执行** | 通过 sub-agents                | 多入口边                  | 手动实现                 |
| **持久化**   | 可选                           | Checkpointer              | Checkpointer             |
| **流式输出** | 支持                           | 5 种 stream_mode          | 支持                     |
| **适用场景** | 研究类任务                     | 复杂拓扑                  | 线性工作流               |

## 核心混合架构（推荐）

**最佳实践**：LangGraph 主图（编排高层拓扑） + Deep Agent 节点（处理复杂子任务）

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent

# Deep Agent 作为节点
research_agent = create_deep_agent(model, tools, system_prompt)

def research_node(state):
    result = research_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"research_result": result["messages"][-1].content}

# LangGraph 主图编排
builder = StateGraph(MainState)
builder.add_node("research", research_node)
builder.add_edge(START, "research")
builder.add_edge("research", END)
graph = builder.compile()
```

详见: `00_quickstart/deep_agent_as_node.md`

## Anti-Patterns 警告

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
# ❌ 错误：直接传递 Deep Agent 内部状态到主图
def node(state):
    result = agent.invoke(...)
    return result  # 泄露内部 messages、files 等

# ✅ 正确：只提取需要的字段
def node(state):
    result = agent.invoke(...)
    return {"summary": result["messages"][-1].content}
```

### ❌ Anti-Pattern 3: 文件系统冲突

```python
# ❌ 错误：多个并行 Deep Agent 写同一文件
agent_a.invoke(...)  # 写 /output/result.txt
agent_b.invoke(...)  # 也写 /output/result.txt → 冲突！

# ✅ 正确：隔离或命名空间
agent_a → /workspace/agent_a/result.txt
agent_b → /workspace/agent_b/result.txt
```

### ❌ Anti-Pattern 4: 滥用 Deep Agent

```python
# ❌ 错误：简单任务用 Deep Agent
email_sender = create_deep_agent(tools=[send_email], system_prompt="发送邮件")

# ✅ 正确：简单任务用普通函数
def send_email_node(state):
    return send_email(state["recipient"], state["body"])
```

## Code Standards

- Follow Deep Research patterns for production systems
- Use temperature=0.0 for deterministic behavior
- Document tool docstrings thoroughly (LLM reads them)
- Structure prompts with explicit workflows
- Only make changes that are directly requested. Keep solutions simple and focused.
- **所有代码示例需标注 LangGraph 版本要求**

## LangGraph 特性映射表

| LangGraph 特性    | 文档位置                                              | 官方文档参考                                      |
| ----------------- | ----------------------------------------------------- | ------------------------------------------------- |
| StateGraph        | `01_atomic/10_graph_api_basics.md`                    | `04_LangGraph_APIs/01_Graph_API_overview.md`      |
| Reducers          | `02_patterns/state_management/`                       | `04_LangGraph_APIs/02_Use_the_graph_API.md`       |
| Conditional Edges | `02_patterns/complex_topology/`                       | 同上                                              |
| Send API          | `02_patterns/send_api_patterns/`                      | 同上                                              |
| Checkpointers     | `01_atomic/08_add_persistence.md`                     | `01_Capabilities/00_Persistence.md`               |
| Memory Store      | `04_langgraph_integration/04_memory_guide.md`         | `01_Capabilities/05_Memory.md`                    |
| Streaming         | `01_atomic/09_add_streaming.md`                       | `01_Capabilities/02_Streaming.md`                 |
| Interrupts        | `02_patterns/human_in_loop/`                          | `01_Capabilities/03_Interrupts.md`                |
| Subgraphs         | `00_quickstart/deep_agent_as_node.md`                 | `01_Capabilities/06_Subgraphs.md`                 |
| Functional API    | `04_langgraph_integration/02_functional_api_guide.md` | `04_LangGraph_APIs/03_Functional_API_overview.md` |
