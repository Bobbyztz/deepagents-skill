# Add Custom Tool

> **📋 Prerequisites:** `01_create_orchestrator.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """Description that LLM will read to understand when to use this tool.

    Args:
        query: What the user is asking about

    Returns:
        Processed result
    """
    return f"Processed: {query}"

# Add to agent
agent = create_deep_agent(
    model=model,
    tools=[my_tool],  # Your tools here
    system_prompt="..."
)
```

---

## 📖 Tool Anatomy

### Key Elements

```python
@tool
def tool_name(
    param1: str,           # Required parameter
    param2: int = 10       # Optional with default
) -> str:                  # Return type
    """One-line summary for the LLM.

    More detailed explanation if needed.
    LLM reads this to decide when to use the tool.

    Args:
        param1: Description of what param1 is
        param2: Description of what param2 is

    Returns:
        Description of what the tool returns
    """
    # Implementation
    return result
```

**Critical**: The docstring is **read by the LLM** to understand:

- What the tool does
- When to use it
- What parameters to provide

---

## 🎯 Real-World Examples

### Web Search Tool

```python
from langchain_core.tools import tool
from tavily import TavilyClient

tavily = TavilyClient()

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for current information.

    Use this when you need up-to-date information about:
    - Recent news or events
    - Current statistics or data
    - Technical documentation

    Args:
        query: The search query (be specific for better results)
        max_results: Maximum number of results to return

    Returns:
        Search results with titles, snippets, and URLs
    """
    results = tavily.search(query, max_results=max_results)

    # Format results for LLM
    output = []
    for r in results.get("results", []):
        output.append(f"**{r['title']}**\n{r['content']}\nURL: {r['url']}\n")

    return "\n---\n".join(output) if output else "No results found."
```

### Think Tool (Reflection)

```python
@tool
def think_tool(reflection: str) -> str:
    """Strategic reflection tool for quality decision-making.

    Use this AFTER each search to:
    - Analyze what you found
    - Identify gaps in your knowledge
    - Decide whether to continue or return findings

    Args:
        reflection: Your detailed thoughts on:
            - What key information did I find?
            - What's still missing?
            - Should I continue or stop?

    Returns:
        Confirmation that reflection was recorded
    """
    return f"Reflection recorded: {reflection}"
```

### Calculator Tool

```python
@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions.

    Args:
        expression: Math expression like "2 + 3 * 4" or "sqrt(16)"

    Returns:
        The numerical result
    """
    import math

    # Safe evaluation (in production, use a proper math parser)
    allowed = {"__builtins__": None, "math": math}
    try:
        result = eval(expression, allowed, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"
```

---

## 🔧 For LangGraph (Non-Deep Agents)

Bind tools to model and create tool node:

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

model = init_chat_model("openai:gpt-4o")
tools = [add]

# Bind tools to model
model_with_tools = model.bind_tools(tools)

# Create tool execution node
tools_by_name = {t.name: t for t in tools}

def tool_node(state):
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return {"messages": results}
```

---

## 🐛 Troubleshooting

### Tool not being used

1. **Check docstring** - Make it clear when to use the tool
2. **Be explicit in prompt**:
   ```python
   "When you need to search, use the web_search tool"
   ```

### Tool errors

```python
@tool
def safe_tool(param: str) -> str:
    """..."""
    try:
        result = risky_operation(param)
        return str(result)
    except Exception as e:
        return f"Tool error: {e}"  # Return error as string, don't raise
```

---

## 🔗 Next Steps

**Configure sub-agents:**
→ `03_configure_subagent.md`

**Add streaming to tools:**
→ `09_add_streaming.md`

---

## 💡 Key Takeaways

1. **Docstrings are critical** - LLM reads them
2. **Return strings** - even for structured data
3. **Handle errors gracefully** - return error message, don't crash
4. For LangGraph, **bind tools to model** with `bind_tools()`
