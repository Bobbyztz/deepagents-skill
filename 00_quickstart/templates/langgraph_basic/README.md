# Basic LangGraph Agent Template

> **LangGraph Version**: `>=0.2.0`

## Quick Start

1. **Copy this directory** to your project
2. **Install dependencies**:
   ```bash
   pip install langgraph langchain langchain-anthropic
   ```
3. **Set your API key**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
4. **Run**:
   ```bash
   python agent.py
   ```

## What You Get

This template demonstrates:

- ✅ StateGraph setup
- ✅ State with reducers (message accumulation)
- ✅ LLM node with tool binding
- ✅ Tool execution node
- ✅ Conditional routing (tools vs end)
- ✅ ReAct-style loop

## File Structure

```
langgraph_basic/
├── agent.py       # Main agent definition
└── README.md      # This file
```

## Customization

### Add More Tools

```python
@tool
def my_tool(param: str) -> str:
    """Tool description for LLM"""
    return result

tools = [calculator, get_weather, my_tool]  # Add here
```

### Change Routing Logic

```python
def should_continue(state: AgentState) -> Literal["tool_node", "other_node", "__end__"]:
    # Your custom logic
    if some_condition:
        return "other_node"
    return END
```

### Add Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = builder.compile(checkpointer=checkpointer)

# Use with thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke(input, config)
```

### Add Streaming

```python
for chunk in agent.stream({"messages": [HumanMessage("Hello")]}):
    print(chunk)
```

## Graph Structure

```
START → llm_node → (has tool calls?) → tool_node → llm_node (loop)
                 → (no tools)       → END
```

## Next Steps

- **Add persistence**: See `deepagents_skills_v2/01_atomic/08_add_persistence.md`
- **Add streaming**: See `deepagents_skills_v2/01_atomic/09_add_streaming.md`
- **Complex topology**: See `deepagents_skills_v2/02_patterns/complex_topology/`
- **Use Deep Agent as node**: See `templates/hybrid_agent/`
