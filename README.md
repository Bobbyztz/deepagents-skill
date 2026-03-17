# deepagents-skill

AI-optimized skills for building multi-agent systems with [Deep Agents](https://github.com/deep-agents) and [LangGraph](https://github.com/langchain-ai/langgraph) (`>=0.2.0`).

## Three paths

| Path | When to use | Key API |
|------|-------------|---------|
| **Deep Agents** | Medium complexity, 15 lines to a working agent | `create_deep_agent()` — built-in planning, filesystem, sub-agents |
| **LangGraph Graph API** | Full topology control | `StateGraph` + nodes + edges + reducers |
| **LangGraph Functional API** | Minimal boilerplate | `@entrypoint` + `@task` decorators |

## Structure

```
deepagents-skill/
├── 00_quickstart/          # 4 template projects — copy and run
├── 01_atomic/              # 11 single-purpose operation guides
├── 02_patterns/            # 9 design patterns (reflection, parallel delegation, etc.)
├── 03_examples/            # Full projects (deep research, hybrid multi-agent)
├── 04_langgraph_integration/  # LangGraph-specific guides
├── ROUTER.md               # Decision tree — start here
└── deepagents-rules.md     # Project rules for AI assistants
```

## Usage

**For AI assistants (Cursor / GitHub Copilot / Claude):** point the assistant at `ROUTER.md` — it contains a decision tree to locate the exact file needed.

**For humans:** browse `00_quickstart/` to get started, or read `ROUTER.md` for the full map.

> The atomic skills are structured tutorials, not executable units — they don't take parameters and output code. The agent reads, understands, and decides how to act. Opus and Sonnet handle this well.

## License

[MIT](LICENSE)
