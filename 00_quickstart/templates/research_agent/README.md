# Research Agent Template

> **LangGraph Version**: `>=0.2.0`

A production-ready research agent based on the Deep Research pattern.

## Quick Start

1. **Copy this directory** to your project
2. **Install dependencies**:
   ```bash
   pip install deepagents langgraph>=0.2.0 tavily-python
   ```
3. **Set your API keys**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export TAVILY_API_KEY="tvly-..."  # For web search
   ```
4. **Implement web_search** in `tools.py` (see TODO comments)
5. **Run**:
   ```bash
   python agent.py
   ```

## Architecture

```
User Query
    ↓
Orchestrator (main agent)
    ├─ Plan: Creates TODO list
    ├─ Save Request: Writes to /research_request.md
    ├─ Delegate: Spawns research sub-agents
    │      ↓
    │  Research Sub-agent(s)
    │      ├─ web_search → results
    │      ├─ think_tool → reflection
    │      └─ Returns findings with citations
    │      ↓
    ├─ Synthesize: Consolidates findings
    ├─ Write Report: /final_report.md
    └─ Verify: Confirms coverage
        ↓
    Final Report
```

## What You Get

- ✅ Planning workflow (write_todos)
- ✅ File system for context management
- ✅ Context isolation via sub-agents
- ✅ Reflection loop (think_tool)
- ✅ Professional citation handling
- ✅ Configurable limits

## File Structure

```
research_agent/
├── agent.py       # Main agent definition
├── prompts.py     # Orchestrator and researcher prompts
├── tools.py       # web_search and think_tool
└── README.md      # This file
```

## Customization

### Change Search Provider

In `tools.py`, replace the placeholder with your search API:

```python
from tavily import TavilyClient

tavily = TavilyClient()

@tool
def web_search(query: str, max_results: int = 3) -> str:
    results = tavily.search(query, max_results=max_results)
    # Format results...
```

### Adjust Limits

In `agent.py`:

```python
MAX_CONCURRENT_SUBAGENTS = 3  # Max parallel sub-agents
MAX_ITERATIONS = 3            # Max delegation rounds
```

### Modify Prompts

Edit `prompts.py` to change:

- Workflow steps
- Delegation strategy
- Report format

## Next Steps

- **Understand the architecture**: See `deepagents_skills_v2/03_examples/deep_research/`
- **Learn about sub-agents**: See `deepagents_skills_v2/01_atomic/03_configure_subagent.md`
- **Learn about think_tool**: See `deepagents_skills_v2/02_patterns/reflection_loop/`
- **Use in hybrid architecture**: See `templates/hybrid_agent/`
