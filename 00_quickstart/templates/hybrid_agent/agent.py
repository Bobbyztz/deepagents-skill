"""Hybrid Agent Template: LangGraph + Deep Agents

Demonstrates the recommended architecture:
- LangGraph StateGraph for high-level orchestration
- Deep Agent nodes for complex sub-tasks

This template shows:
1. Multiple Deep Agents as LangGraph nodes
2. State mapping between graph and agents
3. Sequential and conditional execution

LangGraph Version: >=0.2.0
"""

from typing import Literal
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent
from agents import research_agent, analysis_agent
from state import MainState

# ============================================================================
# Configuration
# ============================================================================

MODEL = "anthropic:claude-sonnet-4-5-20250929"
TEMPERATURE = 0.0

# ============================================================================
# Node Functions (State Mapping)
# ============================================================================

def research_node(state: MainState) -> dict:
    """Execute research using Deep Agent.
    
    Maps MainState → Deep Agent input → Deep Agent output → MainState update
    """
    # Input mapping
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    
    # Output mapping - only extract what we need
    return {
        "research_result": result["messages"][-1].content,
        "stage": "analysis"
    }


def analysis_node(state: MainState) -> dict:
    """Execute analysis using Deep Agent.
    
    Uses research_result from previous step.
    """
    prompt = f"Analyze the following research findings:\n\n{state['research_result']}"
    
    result = analysis_agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    
    return {
        "analysis_result": result["messages"][-1].content,
        "stage": "complete"
    }


def summarize_node(state: MainState) -> dict:
    """Simple summarization node (not a Deep Agent).
    
    Demonstrates mixing Deep Agent nodes with regular nodes.
    """
    summary = f"""## Summary

### Research Findings
{state['research_result'][:500]}...

### Analysis
{state['analysis_result'][:500]}...
"""
    return {"final_output": summary}


# ============================================================================
# Routing Logic
# ============================================================================

def should_analyze(state: MainState) -> Literal["analysis", "summarize"]:
    """Decide whether to run analysis or skip to summary."""
    # Example condition: skip analysis for simple queries
    if len(state.get("research_result", "")) < 100:
        return "summarize"
    return "analysis"


# ============================================================================
# Graph Construction
# ============================================================================

def create_graph():
    """Build the hybrid LangGraph + Deep Agents graph."""
    builder = StateGraph(MainState)
    
    # Add nodes
    builder.add_node("research", research_node)      # Deep Agent node
    builder.add_node("analysis", analysis_node)      # Deep Agent node
    builder.add_node("summarize", summarize_node)    # Regular node
    
    # Define flow
    builder.add_edge(START, "research")
    builder.add_conditional_edges("research", should_analyze)
    builder.add_edge("analysis", "summarize")
    builder.add_edge("summarize", END)
    
    return builder.compile()


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    graph = create_graph()
    
    # Example query
    result = graph.invoke({
        "query": "What are the latest developments in quantum computing?",
        "research_result": None,
        "analysis_result": None,
        "final_output": None,
        "stage": "research"
    })
    
    print("=== Final Output ===")
    print(result["final_output"])
    
    # Visualize the graph (optional)
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        print("\n=== Graph Structure ===")
        print(graph.get_graph().draw_mermaid())
