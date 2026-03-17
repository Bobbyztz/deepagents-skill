# Hybrid Agent Template: LangGraph + Deep Agents

> **LangGraph Version**: `>=0.2.0`

The **recommended architecture** for complex agent systems.

## Why Hybrid?

| Pure Deep Agents     | Pure LangGraph          | Hybrid (This Template) |
| -------------------- | ----------------------- | ---------------------- |
| ✅ Built-in planning | ✅ Complex topology     | ✅ Both!               |
| ✅ File system       | ✅ Parallel execution   | ✅ Both!               |
| ❌ Limited topology  | ❌ No built-in planning | ✅ Both!               |

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

## Architecture

```
LangGraph Main Graph
    │
    ├── research_node (Deep Agent)
    │   ├── Planning
    │   ├── Web search
    │   └── think_tool
    │
    ├── analysis_node (Deep Agent)
    │   ├── Data analysis
    │   └── think_tool
    │
    └── summarize_node (Regular function)
        └── Simple synthesis
```

## File Structure

```
hybrid_agent/
├── agent.py       # Main graph definition & nodes
├── agents.py      # Deep Agent definitions
├── state.py       # MainState TypedDict
└── README.md      # This file
```

## Key Concepts

### 1. State Mapping

Deep Agents use `{"messages": [...]}` format.
Main graph uses custom state.

```python
def research_node(state: MainState) -> dict:
    # Input mapping: MainState → Deep Agent format
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })

    # Output mapping: Only extract what we need
    return {"research_result": result["messages"][-1].content}
```

### 2. Mixing Node Types

Not every node needs to be a Deep Agent:

```python
builder.add_node("research", research_node)      # Deep Agent
builder.add_node("analysis", analysis_node)      # Deep Agent
builder.add_node("summarize", summarize_node)    # Regular function
```

### 3. Conditional Routing

Use LangGraph's conditional edges for dynamic flow:

```python
def should_analyze(state) -> Literal["analysis", "summarize"]:
    if some_condition:
        return "analysis"
    return "summarize"

builder.add_conditional_edges("research", should_analyze)
```

## Customization

### Add More Deep Agents

In `agents.py`:

```python
writing_agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="You are a writing specialist..."
)
```

In `agent.py`:

```python
def writing_node(state: MainState) -> dict:
    result = writing_agent.invoke(...)
    return {"written_output": result["messages"][-1].content}

builder.add_node("writing", writing_node)
```

### Add Parallel Execution

```python
# Fan-out: Multiple edges from same source
builder.add_edge(START, "research_tech")
builder.add_edge(START, "research_market")

# Fan-in: Multiple edges to same target
builder.add_edge("research_tech", "summarize")
builder.add_edge("research_market", "summarize")
```

### Add Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Use with thread_id
result = graph.invoke(input, {"configurable": {"thread_id": "user-123"}})
```

## Anti-Patterns to Avoid

❌ **Don't nest Deep Agents inside Deep Agents**

```python
# Bad: Deep Agent as sub-agent of another Deep Agent
main_agent = create_deep_agent(
    subagents=[another_deep_agent]  # ❌
)

# Good: Flat structure with LangGraph
builder.add_node("agent_a", agent_a_node)
builder.add_node("agent_b", agent_b_node)  # ✅
```

❌ **Don't leak internal state**

```python
# Bad
return result  # Leaks messages, files, todos

# Good
return {"summary": result["messages"][-1].content}
```

## Next Steps

- **Learn more patterns**: `deepagents_skills_v2/02_patterns/complex_topology/`
- **Add Send API**: `deepagents_skills_v2/02_patterns/send_api_patterns/`
- **Production guide**: `deepagents_skills_v2/04_langgraph_integration/06_production_guide.md`
