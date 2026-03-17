"""Basic Deep Agent Template

A minimal Deep Agent with one custom tool.
Copy this directory and modify for your use case.

LangGraph Version: >=0.2.0
"""

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from deepagents import create_deep_agent

# ============================================================================
# Configuration
# ============================================================================

# Model selection
MODEL = "anthropic:claude-sonnet-4-5-20250929"
TEMPERATURE = 0.0

# System prompt
SYSTEM_PROMPT = """You are a helpful assistant.

You have access to tools to help users complete their tasks.
Always think step-by-step and use tools when appropriate.
"""

# ============================================================================
# Custom Tools
# ============================================================================

@tool
def example_tool(query: str) -> str:
    """An example tool that does something useful.
    
    Args:
        query: The input query string
        
    Returns:
        A processed result
    """
    # TODO: Replace with your actual tool logic
    return f"Processed: {query}"


# ============================================================================
# Agent Creation
# ============================================================================

def create_agent():
    """Create and return the configured agent."""
    model = init_chat_model(MODEL, temperature=TEMPERATURE)
    
    agent = create_deep_agent(
        model=model,
        tools=[example_tool],  # Add your tools here
        system_prompt=SYSTEM_PROMPT
    )
    
    return agent


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    agent = create_agent()
    
    # Example usage
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Hello! Can you help me?"}]
    })
    
    # Print the response
    print(result["messages"][-1].content)
    
    # Print any files created
    if result.get("files"):
        print("\nFiles created:")
        for path in result["files"].keys():
            print(f"  - {path}")
