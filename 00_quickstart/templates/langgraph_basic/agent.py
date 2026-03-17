"""Basic LangGraph Agent Template

A minimal LangGraph agent with StateGraph.
Copy this directory and modify for your use case.

LangGraph Version: >=0.2.0
"""

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from typing import Literal
import operator

# ============================================================================
# Configuration
# ============================================================================

MODEL = "anthropic:claude-sonnet-4-5-20250929"
TEMPERATURE = 0.0

SYSTEM_PROMPT = "You are a helpful assistant. Use tools when appropriate."

# ============================================================================
# Tools
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A math expression like "2 + 3" or "10 * 5"
    
    Returns:
        The result as a string
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_weather(location: str) -> str:
    """Get weather for a location (mock implementation).
    
    Args:
        location: City name
    
    Returns:
        Weather description
    """
    # TODO: Replace with actual weather API
    return f"Weather in {location}: Sunny, 22°C"


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State that flows through the graph."""
    messages: Annotated[list[AnyMessage], operator.add]


# ============================================================================
# Node Functions
# ============================================================================

# Setup
model = init_chat_model(MODEL, temperature=TEMPERATURE)
tools = [calculator, get_weather]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)


def llm_node(state: AgentState) -> dict:
    """Call the LLM to decide next action."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    """Execute tool calls from the last message."""
    last_message = state["messages"][-1]
    results = []
    
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    
    return {"messages": results}


# ============================================================================
# Routing Logic
# ============================================================================

def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    """Decide whether to continue to tools or end."""
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        return "tool_node"
    
    return END


# ============================================================================
# Graph Construction
# ============================================================================

def create_agent():
    """Build and compile the agent graph."""
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("llm_node", llm_node)
    builder.add_node("tool_node", tool_node)
    
    # Add edges
    builder.add_edge(START, "llm_node")
    builder.add_conditional_edges("llm_node", should_continue, ["tool_node", END])
    builder.add_edge("tool_node", "llm_node")
    
    # Compile
    return builder.compile()


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    agent = create_agent()
    
    # Example usage
    result = agent.invoke({
        "messages": [HumanMessage(content="What is 15 * 7?")]
    })
    
    # Print conversation
    print("=== Conversation ===")
    for msg in result["messages"]:
        msg.pretty_print()
