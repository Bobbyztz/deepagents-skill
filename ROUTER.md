# Deep Agents Skills V2 Router

> **🤖 For AI Assistants (Cursor/GitHub Copilot):**  
> This is your navigation guide. **Read this file FIRST**, then follow the decision tree to load ONLY relevant files.
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 START HERE: What Should I Read?

### Step 1: Determine Your Starting Point

#### 🆕 Never used Deep Agents or LangGraph before?

```
选择你的学习路径:

A) 想用 Deep Agents 快速开始:
   1. Read `00_quickstart/what_is_deep_agents.md` (5 min)
   2. Read `00_quickstart/minimal_example.md` (10 min)
   3. Copy `00_quickstart/templates/basic_agent/`

B) 想用纯 LangGraph 开始:
   1. Read `00_quickstart/langgraph_quickstart.md` (10 min)
   2. Copy `00_quickstart/templates/langgraph_basic/`

C) 想了解两者结合:
   1. Read `00_quickstart/architecture_comparison.md` (10 min)
   2. Read `00_quickstart/deep_agent_as_node.md` (15 min)【核心】
   3. Copy `00_quickstart/templates/hybrid_agent/`
```

#### ✅ Already understand the basics?

→ Continue to Step 2

---

### Step 2: Identify Your Task Type

#### 🆕 **Type A: Building a New Agent from Scratch**

##### A1. 最简单的 Agent（Deep Agents）

```
→ Copy `00_quickstart/templates/basic_agent/`
→ Modify `agent.py` with your model and tools
→ Done!
```

##### A2. 研究类 Agent（Deep Agents）

```
→ Copy `00_quickstart/templates/research_agent/`
→ Read `03_examples/deep_research/00_overview.md` to understand architecture
→ Customize based on your needs
```

##### A3. 纯 LangGraph Agent

```
→ Copy `00_quickstart/templates/langgraph_basic/`
→ Read `04_langgraph_integration/01_graph_api_guide.md` for customization
→ Build your workflow
```

##### A4. 混合架构 Agent【推荐复杂场景】

```
→ Copy `00_quickstart/templates/hybrid_agent/`
→ Read `00_quickstart/deep_agent_as_node.md` 【核心】
→ Read `02_patterns/complex_topology/README.md` for advanced patterns
```

##### A5. 想完全理解每个组件再构建

```
→ Read `00_quickstart/architecture_comparison.md` first
→ Then read files in `01_atomic/` in order (01 → 11)
→ Each file teaches one atomic operation
→ Then assemble your agent
```

---

#### ➕ **Type B: Adding Features to Existing Agent**

**Decision Table:**

| I want to add...          | Deep Agents 方式                         | LangGraph 方式                                     | Prerequisites                             |
| ------------------------- | ---------------------------------------- | -------------------------------------------------- | ----------------------------------------- |
| **Custom tool**           | `01_atomic/02_add_tool.md`               | 同文件                                             | None                                      |
| **Sub-agent**             | `01_atomic/03_configure_subagent.md`     | `02_patterns/context_isolation/`                   | `02_patterns/context_isolation/README.md` |
| **File system**           | `01_atomic/04_setup_filesystem.md`       | N/A                                                | None                                      |
| **Planning (TODO lists)** | `01_atomic/05_enable_planning.md`        | N/A                                                | `02_patterns/planning_workflow/`          |
| **Human approval**        | `01_atomic/06_add_human_in_loop.md`      | `02_patterns/human_in_loop/`                       | None                                      |
| **Long-term memory**      | `01_atomic/07_add_long_term_memory.md`   | `04_langgraph_integration/04_memory_guide.md`      | `01_atomic/04_setup_filesystem.md`        |
| **Persistence**           | `01_atomic/08_add_persistence.md`        | `04_langgraph_integration/03_persistence_guide.md` | None                                      |
| **Streaming**             | `01_atomic/09_add_streaming.md`          | `04_langgraph_integration/05_streaming_guide.md`   | None                                      |
| **Graph API basics**      | N/A                                      | `01_atomic/10_graph_api_basics.md`                 | None                                      |
| **Deep Agent as node**    | `01_atomic/11_use_deep_agent_as_node.md` | 同文件【核心】                                     | `00_quickstart/deep_agent_as_node.md`     |

---

#### 🧠 **Type C: Understanding Design Patterns**

**Pattern Catalog:**

| I want to understand...  | Read this directory                          | Use case                              |
| ------------------------ | -------------------------------------------- | ------------------------------------- |
| **Why use sub-agents?**  | `02_patterns/context_isolation/`             | Keep orchestrator context clean       |
| **How think_tool works** | `02_patterns/reflection_loop/`               | Quality-driven search                 |
| **6-step workflow**      | `02_patterns/planning_workflow/`             | Plan → Execute → Verify pattern       |
| **When to parallelize**  | `02_patterns/parallel_delegation/`           | Comparison queries, independent tasks |
| **State management**     | `02_patterns/state_management/` 【新增】     | Reducers, TypedDict, state updates    |
| **Complex topology**     | `02_patterns/complex_topology/` 【核心新增】 | 一父多子、子间拓扑、并行扇出          |
| **Dynamic branching**    | `02_patterns/send_api_patterns/` 【新增】    | Map-Reduce, Send API                  |
| **Human-in-the-loop**    | `02_patterns/human_in_loop/` 【新增】        | interrupt(), approval workflows       |
| **Hybrid architecture**  | `02_patterns/hybrid_architecture/` 【新增】  | LangGraph + Deep Agents 组合          |

**Each pattern directory contains:**

- `README.md` - Concept, motivation, when to use
- Implementation examples with code
- Real-world application cases

---

#### 📚 **Type D: Learning from Complete Examples**

**Deep Research Walkthrough (Deep Agents):**

```
Start: `03_examples/deep_research/00_overview.md`
Then read in order:
  01_architecture.md       → Understand 3-layer design
  02_file_walkthrough.md   → What each file does
  03_execution_flow.md     → How a request is processed
  04_prompt_system.md      → Orchestrator vs worker prompts
  05_tool_implementation.md → Tavily + think_tool deep dive
```

**LangGraph Chatbot (Pure LangGraph):**【新增】

```
Start: `03_examples/langgraph_chatbot/README.md`
→ Complete StateGraph chatbot with persistence
```

**Functional API Workflow:**【新增】

```
Start: `03_examples/functional_api_workflow/README.md`
→ @entrypoint + @task workflow example
```

**Hybrid Multi-Agent System:**【核心新增】

```
Start: `03_examples/hybrid_multi_agent/README.md`
→ LangGraph 主图 + Deep Agent 节点
→ 展示复杂拓扑实现
```

---

#### 🔧 **Type E: LangGraph Deep Integration**【新增模块】

| I want to learn...          | Read this file                                        |
| --------------------------- | ----------------------------------------------------- |
| **LangGraph 概览**          | `04_langgraph_integration/00_overview.md`             |
| **Graph API 完整指南**      | `04_langgraph_integration/01_graph_api_guide.md`      |
| **Functional API 完整指南** | `04_langgraph_integration/02_functional_api_guide.md` |
| **持久化 (Checkpointers)**  | `04_langgraph_integration/03_persistence_guide.md`    |
| **内存管理 (Memory Store)** | `04_langgraph_integration/04_memory_guide.md`         |
| **流式输出详解**            | `04_langgraph_integration/05_streaming_guide.md`      |
| **生产部署**                | `04_langgraph_integration/06_production_guide.md`     |
| **迁移指南**                | `04_langgraph_integration/07_migration_guide.md`      |

---

## 🧭 Navigation Tips

### Every File Has:

- **📋 Prerequisites** - What to read first
- **⚡ Quick Answer** - Copy-paste ready code
- **📖 Step-by-Step** - Detailed explanation
- **🔗 Next Steps** - Where to go after

### Dependency Check:

If a file mentions a prerequisite you haven't read, **stop and read that first**.

### Version Check:

All code examples require `langgraph>=0.2.0`. Check your version before running.

---

## 📂 Directory Structure Overview

```
deepagents_skills_v2/
├── ROUTER.md                           # ← YOU ARE HERE
├── deepagents-rules.md                 # Project rules
│
├── 00_quickstart/                      # Fast path to working agent
│   ├── what_is_deep_agents.md         # Deep Agents 介绍
│   ├── minimal_example.md             # 最小示例
│   ├── langgraph_quickstart.md        # 【新增】纯LangGraph快速入门
│   ├── architecture_comparison.md      # 【新增】三种架构对比
│   ├── deep_agent_as_node.md          # 【核心】Deep Agent作为节点
│   └── templates/
│       ├── basic_agent/               # 基础 Deep Agent 模板
│       ├── research_agent/            # 研究类 Agent 模板
│       ├── langgraph_basic/           # 【新增】纯LangGraph模板
│       └── hybrid_agent/              # 【新增】混合架构模板
│
├── 01_atomic/                          # Single-purpose operations
│   ├── 01_create_orchestrator.md
│   ├── 02_add_tool.md
│   ├── 03_configure_subagent.md
│   ├── 04_setup_filesystem.md
│   ├── 05_enable_planning.md
│   ├── 06_add_human_in_loop.md
│   ├── 07_add_long_term_memory.md
│   ├── 08_add_persistence.md          # 【新增】
│   ├── 09_add_streaming.md            # 【新增】
│   ├── 10_graph_api_basics.md         # 【新增】
│   └── 11_use_deep_agent_as_node.md   # 【核心】
│
├── 02_patterns/                        # Design patterns
│   ├── context_isolation/
│   ├── reflection_loop/
│   ├── planning_workflow/
│   ├── parallel_delegation/
│   ├── state_management/              # 【新增】
│   ├── complex_topology/              # 【核心】
│   ├── send_api_patterns/             # 【新增】
│   ├── human_in_loop/                 # 【新增】
│   └── hybrid_architecture/           # 【新增】
│
├── 03_examples/                        # Complete projects
│   ├── deep_research/                 # Deep Agents 示例
│   ├── langgraph_chatbot/             # 【新增】
│   ├── functional_api_workflow/       # 【新增】
│   └── hybrid_multi_agent/            # 【核心】
│
└── 04_langgraph_integration/          # 【新增】LangGraph深度整合
    ├── 00_overview.md
    ├── 01_graph_api_guide.md
    ├── 02_functional_api_guide.md
    ├── 03_persistence_guide.md
    ├── 04_memory_guide.md
    ├── 05_streaming_guide.md
    ├── 06_production_guide.md
    └── 07_migration_guide.md
```

---

## 🚀 Recommended Learning Paths

### Path 1: Quick Start with Deep Agents (30 min)

```
00_quickstart/what_is_deep_agents.md
→ 00_quickstart/minimal_example.md
→ Copy templates/basic_agent/
→ Start building!
```

### Path 2: Quick Start with LangGraph (30 min)

```
00_quickstart/langgraph_quickstart.md
→ 01_atomic/10_graph_api_basics.md
→ Copy templates/langgraph_basic/
→ Start building!
```

### Path 3: Master Hybrid Architecture (2 hours)【推荐】

```
00_quickstart/architecture_comparison.md
→ 00_quickstart/deep_agent_as_node.md【核心】
→ 02_patterns/complex_topology/README.md
→ 02_patterns/hybrid_architecture/README.md
→ 03_examples/hybrid_multi_agent/README.md
→ Copy templates/hybrid_agent/
```

### Path 4: Deep Understanding (4-5 hours)

```
00_quickstart/what_is_deep_agents.md
→ 00_quickstart/architecture_comparison.md
→ All files in 01_atomic/ (in order)
→ All patterns in 02_patterns/ (based on interest)
→ 03_examples/deep_research/ (complete walkthrough)
→ 04_langgraph_integration/ (selective based on needs)
```

### Path 5: LangGraph Deep Dive (3 hours)

```
00_quickstart/langgraph_quickstart.md
→ 04_langgraph_integration/00_overview.md
→ 04_langgraph_integration/01_graph_api_guide.md
→ 04_langgraph_integration/02_functional_api_guide.md
→ 02_patterns/state_management/README.md
→ 02_patterns/complex_topology/README.md
```

---

## ❓ Quick FAQ Router

**Q: I just want to copy working code**  
A: `00_quickstart/templates/` - choose basic_agent, research_agent, langgraph_basic, or hybrid_agent

**Q: Deep Agents vs LangGraph - which to use?**  
A: `00_quickstart/architecture_comparison.md` → comprehensive comparison

**Q: How to add a web search tool?**  
A: `01_atomic/02_add_tool.md` → See "Real-World Example: tavily_search"

**Q: Why is my agent's context too long?**  
A: `02_patterns/context_isolation/README.md` → Learn about sub-agents

**Q: How do I make my agent think before acting?**  
A: `02_patterns/reflection_loop/` → Learn the think_tool pattern

**Q: I want to build exactly like Deep Research**  
A: `03_examples/deep_research/00_overview.md` → Start here

**Q: How to persist conversation state?**  
A: `01_atomic/08_add_persistence.md` or `04_langgraph_integration/03_persistence_guide.md`

**Q: How to stream LLM output?**  
A: `01_atomic/09_add_streaming.md` or `04_langgraph_integration/05_streaming_guide.md`

**Q: How to implement human-in-the-loop?**  
A: `02_patterns/human_in_loop/README.md` → interrupt() pattern

**Q: How to run multiple agents in parallel?**  
A: `02_patterns/complex_topology/README.md` → fan-out/fan-in pattern

**Q: How to use Deep Agent inside LangGraph?**【常见】  
A: `00_quickstart/deep_agent_as_node.md` → **核心指南**

**Q: How to implement dynamic task distribution?**  
A: `02_patterns/send_api_patterns/README.md` → Send API pattern

---

## 🔑 Key API Quick Reference

```python
# === Deep Agents ===
from deepagents import create_deep_agent
agent = create_deep_agent(model, tools, system_prompt, subagents)
result = agent.invoke({"messages": [...]})

# === LangGraph Graph API ===
from langgraph.graph import StateGraph, START, END
builder = StateGraph(MyState)
builder.add_node("name", node_func)
builder.add_edge(START, "name")
builder.add_conditional_edges("name", route_func)
graph = builder.compile(checkpointer=checkpointer)

# === LangGraph Functional API ===
from langgraph.func import entrypoint, task
@entrypoint(checkpointer=checkpointer)
def workflow(input): ...
@task
def subtask(data): ...

# === Send API (动态分支) ===
from langgraph.types import Send
def distribute(state):
    return [Send("target_node", {"item": i}) for i in state["items"]]

# === Interrupt (人机交互) ===
from langgraph.types import interrupt, Command
approved = interrupt({"question": "批准？"})
graph.invoke(Command(resume=True), config)

# === Streaming ===
for chunk in graph.stream(input, stream_mode="updates"): ...
for chunk in graph.stream(input, stream_mode="messages"): ...
for chunk in graph.stream(input, subgraphs=True): ...
```

---

**Now go to your task type above and follow the path! ⬆️**
