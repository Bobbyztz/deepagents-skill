"""Research Agent Template (Simplified Deep Research)

A production-ready research agent with:
- Web search capabilities
- Strategic reflection (think_tool)
- Research sub-agent for context isolation
- Professional report generation

Based on the official deep_research example.

LangGraph Version: >=0.2.0
"""

from datetime import datetime
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from tools import web_search, think_tool
from prompts import ORCHESTRATOR_INSTRUCTIONS, RESEARCHER_INSTRUCTIONS

# ============================================================================
# Configuration
# ============================================================================

MODEL = "anthropic:claude-sonnet-4-5-20250929"
TEMPERATURE = 0.0

# Limits
MAX_CONCURRENT_SUBAGENTS = 3
MAX_ITERATIONS = 3

current_date = datetime.now().strftime("%Y-%m-%d")

# ============================================================================
# Sub-agent Configuration
# ============================================================================

research_subagent = {
    "name": "research-agent",
    "description": "Delegate research tasks to this agent. Give it one focused topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [web_search, think_tool]
}

# ============================================================================
# Agent Creation
# ============================================================================

def create_agent():
    """Create and return the research agent."""
    model = init_chat_model(MODEL, temperature=TEMPERATURE)
    
    # Format orchestrator instructions with limits
    instructions = ORCHESTRATOR_INSTRUCTIONS.format(
        max_concurrent=MAX_CONCURRENT_SUBAGENTS,
        max_iterations=MAX_ITERATIONS
    )
    
    agent = create_deep_agent(
        model=model,
        tools=[web_search, think_tool],  # Orchestrator has same tools (but shouldn't use for research)
        system_prompt=instructions,
        subagents=[research_subagent]
    )
    
    return agent


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    agent = create_agent()
    
    # Example research query
    query = "Compare Python vs JavaScript for web development"
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # Print the final report
    if "/final_report.md" in result.get("files", {}):
        print("=== Research Report ===\n")
        print(result["files"]["/final_report.md"])
    else:
        print(result["messages"][-1].content)
