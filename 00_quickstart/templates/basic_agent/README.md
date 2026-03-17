# Basic Deep Agent Template

> **LangGraph Version**: `>=0.2.0`

## Quick Start

1. **Copy this directory** to your project
2. **Install dependencies**:
   ```bash
   pip install deepagents langgraph>=0.2.0
   ```
3. **Set your API key**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
4. **Run**:
   ```bash
   python agent.py
   ```

## Customization

### Change the Model

In `agent.py`, modify:

```python
MODEL = "openai:gpt-4o"  # or "google:gemini-3-pro-preview"
```

### Add Your Custom Tool

Replace `example_tool` with your logic:

```python
@tool
def my_tool(query: str) -> str:
    """Description of what your tool does"""
    # Your implementation here
    return result
```

### Modify System Prompt

Edit the `SYSTEM_PROMPT` variable to guide agent behavior.

## What You Get

This template gives you:

- ✅ Planning capabilities (`write_todos`)
- ✅ File system (`read_file`, `write_file`, etc.)
- ✅ Sub-agent spawning (`task`)
- ✅ One example custom tool

## File Structure

```
basic_agent/
├── agent.py       # Main agent definition
└── README.md      # This file
```

## Next Steps

- **Add more tools**: See `deepagents_skills_v2/01_atomic/02_add_tool.md`
- **Configure sub-agents**: See `deepagents_skills_v2/01_atomic/03_configure_subagent.md`
- **See a complex example**: Check `templates/research_agent/`
- **Learn hybrid architecture**: See `deepagents_skills_v2/00_quickstart/deep_agent_as_node.md`
