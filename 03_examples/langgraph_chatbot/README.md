# LangGraph Chatbot Example

> **📋 Prerequisites:**
>
> - `00_quickstart/langgraph_quickstart.md`
> - `01_atomic/08_add_persistence.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

A complete **StateGraph chatbot** demonstrating:

- ✅ Conversation memory (persistence)
- ✅ Tool calling (ReAct loop)
- ✅ Streaming responses
- ✅ Human-in-the-loop capability

---

## 📁 Project Structure

```
langgraph_chatbot/
├── README.md          # This file
├── chatbot.py         # Main chatbot implementation
├── tools.py           # Custom tools
└── requirements.txt   # Dependencies
```

---

## 📄 chatbot.py

```python
"""LangGraph Chatbot with Memory and Tools

A production-ready chatbot demonstrating:
- StateGraph for conversation flow
- Checkpointer for memory persistence
- Tool calling with ReAct loop
- Streaming support

LangGraph Version: >=0.2.0
"""

from typing import Literal
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from tools import calculator, get_weather, search_web

# ============================================================================
# Configuration
# ============================================================================

MODEL = "anthropic:claude-sonnet-4-5-20250929"
SYSTEM_PROMPT = """You are a helpful assistant with access to tools.

Available tools:
- calculator: For math calculations
- get_weather: For weather information
- search_web: For web searches

Be concise and helpful. Use tools when appropriate.
"""

# ============================================================================
# Setup
# ============================================================================

model = init_chat_model(MODEL, temperature=0.0)
tools = [calculator, get_weather, search_web]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)

# ============================================================================
# Nodes
# ============================================================================

def agent_node(state: MessagesState) -> dict:
    """Main agent node - decides action or response."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: MessagesState) -> dict:
    """Execute tool calls from the agent."""
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        try:
            result = tool.invoke(tool_call["args"])
        except Exception as e:
            result = f"Error: {e}"

        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": results}


# ============================================================================
# Routing
# ============================================================================

def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    """Route to tools or end based on agent response."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# ============================================================================
# Graph Construction
# ============================================================================

def create_chatbot():
    """Build and compile the chatbot graph."""
    builder = StateGraph(MessagesState)

    # Add nodes
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    # Define flow
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, ["tools", END])
    builder.add_edge("tools", "agent")  # Loop back after tool execution

    # Add memory persistence
    checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)


# ============================================================================
# Main
# ============================================================================

def main():
    chatbot = create_chatbot()

    # Configuration with thread_id for memory
    config = {"configurable": {"thread_id": "user-session-1"}}

    print("=== LangGraph Chatbot ===")
    print("Type 'quit' to exit, 'new' for new conversation\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            break
        elif user_input.lower() == "new":
            # New thread for new conversation
            config["configurable"]["thread_id"] = f"user-session-{id(user_input)}"
            print("[New conversation started]\n")
            continue
        elif not user_input:
            continue

        # Stream response
        print("Assistant: ", end="", flush=True)

        for msg, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config,
            stream_mode="messages"
        ):
            if hasattr(msg, "content") and msg.content:
                print(msg.content, end="", flush=True)

        print("\n")


if __name__ == "__main__":
    main()
```

---

## 📄 tools.py

```python
"""Tools for LangGraph Chatbot"""

from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: Math expression like "2 + 3 * 4" or "sqrt(16)"

    Returns:
        The calculated result
    """
    import math
    allowed = {"__builtins__": None, "math": math, "sqrt": math.sqrt}
    try:
        result = eval(expression, allowed, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {e}"


@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name (e.g., "San Francisco")

    Returns:
        Weather description
    """
    # TODO: Implement with actual weather API
    return f"Weather in {location}: Sunny, 22°C (72°F)"


@tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search query

    Returns:
        Search results summary
    """
    # TODO: Implement with actual search API (Tavily, etc.)
    return f"Search results for '{query}': [Placeholder - implement actual search]"
```

---

## 🚀 Running

```bash
# Install dependencies
pip install langgraph langchain langchain-anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run
python chatbot.py
```

---

## 🎯 Key Features Demonstrated

### 1. Memory (Persistence)

```python
checkpointer = MemorySaver()
chatbot = builder.compile(checkpointer=checkpointer)

# Same thread_id = same conversation memory
config = {"configurable": {"thread_id": "user-123"}}
```

### 2. ReAct Loop

```
User → Agent → (has tools?) → Tools → Agent → Response
              → (no tools)  → Response
```

### 3. Streaming

```python
for msg, metadata in chatbot.stream(input, config, stream_mode="messages"):
    print(msg.content, end="")
```

---

## 🔗 Next Steps

**Add Deep Agents:**
→ `00_quickstart/deep_agent_as_node.md`

**Add human-in-the-loop:**
→ `02_patterns/human_in_loop/README.md`

**Production deployment:**
→ `04_langgraph_integration/06_production_guide.md`
