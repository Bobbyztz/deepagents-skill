# deepagents-skill

面向 AI 助手优化的技能库，用于搭建基于 [Deep Agents](https://github.com/deep-agents) 和 [LangGraph](https://github.com/langchain-ai/langgraph)（`>=0.2.0`）的多智能体系统。

## 三条路径

| 路径 | 适用场景 | 核心 API |
|------|----------|----------|
| **Deep Agents** | 中等复杂度，15 行代码即可运行 | `create_deep_agent()` — 内置规划、文件系统、子智能体 |
| **LangGraph Graph API** | 需要完整拓扑控制 | `StateGraph` + 节点 + 边 + reducers |
| **LangGraph Functional API** | 最少样板代码 | `@entrypoint` + `@task` 装饰器 |

## 目录结构

```
deepagents-skill/
├── 00_quickstart/             # 4 个模板项目 — 复制即用
├── 01_atomic/                 # 11 个单一用途的操作指南
├── 02_patterns/               # 9 种设计模式（反思、并行委派等）
├── 03_examples/               # 完整项目（深度研究、混合多智能体）
├── 04_langgraph_integration/  # LangGraph 专项指南
├── ROUTER.md                  # 决策树 — 从这里开始
└── deepagents-rules.md        # AI 助手项目规则
```

## 使用方式

**AI 助手（Cursor / GitHub Copilot / Claude）：** 将助手指向 `ROUTER.md`，其中包含决策树，可定位到所需的具体文件。

**人类用户：** 从 `00_quickstart/` 开始浏览，或阅读 `ROUTER.md` 获取完整导航。

> 原子技能更接近结构化教程，而非可执行单元 — 它们不接收参数、不直接输出代码。AI 助手需要阅读、理解后自行决定如何行动。Opus 和 Sonnet 可以很好地处理。

## 许可证

[MIT](LICENSE)
