# Hybrid Multi-Agent System Example【核心】

> **📋 Prerequisites:**
>
> - `00_quickstart/deep_agent_as_node.md`
> - `02_patterns/hybrid_architecture/README.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

This example demonstrates the **recommended hybrid architecture**:

- **LangGraph** for high-level orchestration
- **Deep Agents** for complex sub-tasks

```
              ┌──────────────────────┐
              │   LangGraph Main     │
              │   (Orchestration)    │
              └──────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Research   │  │ Analysis   │  │ Writing    │
│ Deep Agent │  │ Deep Agent │  │ Deep Agent │
│ (Planning) │  │ (Planning) │  │ (Planning) │
│ (Files)    │  │ (Files)    │  │ (Files)    │
└────────────┘  └────────────┘  └────────────┘
```

---

## 📁 Project Structure

```
hybrid_multi_agent/
├── README.md          # This file
├── main.py           # Entry point
├── graph.py          # LangGraph orchestration
├── agents.py         # Deep Agent definitions
├── state.py          # State definitions
└── tools.py          # Shared tools
```

---

## 📄 main.py

```python
"""Hybrid Multi-Agent System - Entry Point"""

from graph import create_graph

def main():
    graph = create_graph()

    result = graph.invoke({
        "query": "Analyze the impact of AI on healthcare",
        "research_result": None,
        "analysis_result": None,
        "final_report": None,
        "stage": "research"
    })

    print("=== Final Report ===")
    print(result["final_report"])

if __name__ == "__main__":
    main()
```

---

## 📄 state.py

```python
"""State definitions for the hybrid system."""

from typing import Literal
from typing_extensions import TypedDict

class MainState(TypedDict):
    """State that flows through the main LangGraph."""
    query: str
    research_result: str | None
    analysis_result: str | None
    final_report: str | None
    stage: Literal["research", "analysis", "writing", "complete"]
```

---

## 📄 tools.py

```python
"""Shared tools for all agents."""

from langchain_core.tools import tool

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        Search results with titles and snippets
    """
    # TODO: Implement with actual search API (Tavily, etc.)
    return f"Search results for '{query}': [Placeholder - implement actual search]"

@tool
def think_tool(reflection: str) -> str:
    """Reflect on findings and plan next steps.

    Args:
        reflection: Your analysis of what you found and what to do next

    Returns:
        Acknowledgment
    """
    return f"Reflection recorded: {reflection}"

@tool
def analyze_data(data: str) -> str:
    """Analyze provided data.

    Args:
        data: Data to analyze

    Returns:
        Analysis results
    """
    return f"Analysis of data: [Placeholder - implement actual analysis]"
```

---

## 📄 agents.py

```python
"""Deep Agent definitions."""

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from tools import web_search, think_tool, analyze_data

MODEL = "anthropic:claude-sonnet-4-5-20250929"
model = init_chat_model(MODEL, temperature=0.0)

# === Research Agent ===
research_agent = create_deep_agent(
    model=model,
    tools=[web_search, think_tool],
    system_prompt="""You are a research specialist.

## Instructions
1. Use web_search to find relevant information
2. After each search, use think_tool to evaluate
3. Stop when you have comprehensive findings
4. Return a summary with key points and sources

## Output Format
- Key Finding 1 [source]
- Key Finding 2 [source]
"""
)

# === Analysis Agent ===
analysis_agent = create_deep_agent(
    model=model,
    tools=[analyze_data, think_tool],
    system_prompt="""You are an analysis specialist.

## Instructions
1. Review the provided research findings
2. Identify patterns, implications, and insights
3. Use analyze_data for structured analysis
4. Return actionable insights

## Output Format
- Insight 1: [explanation]
- Insight 2: [explanation]
- Recommendations: [list]
"""
)

# === Writing Agent ===
writing_agent = create_deep_agent(
    model=model,
    tools=[think_tool],
    system_prompt="""You are a professional writer.

## Instructions
1. Review research and analysis
2. Structure a clear, compelling report
3. Use proper formatting and citations
4. Ensure logical flow

## Output Format
# Report Title
## Executive Summary
## Key Findings
## Analysis
## Recommendations
## Conclusion
"""
)
```

---

## 📄 graph.py

```python
"""LangGraph orchestration."""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from state import MainState
from agents import research_agent, analysis_agent, writing_agent

# === Node Functions (State Mapping) ===

def research_node(state: MainState) -> dict:
    """Execute research using Deep Agent."""
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": f"Research: {state['query']}"}]
    })
    return {
        "research_result": result["messages"][-1].content,
        "stage": "analysis"
    }

def analysis_node(state: MainState) -> dict:
    """Execute analysis using Deep Agent."""
    prompt = f"""Analyze the following research findings:

{state['research_result']}

Original query: {state['query']}
"""
    result = analysis_agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    return {
        "analysis_result": result["messages"][-1].content,
        "stage": "writing"
    }

def writing_node(state: MainState) -> dict:
    """Execute writing using Deep Agent."""
    prompt = f"""Write a comprehensive report based on:

## Research
{state['research_result']}

## Analysis
{state['analysis_result']}

Original query: {state['query']}
"""
    result = writing_agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    return {
        "final_report": result["messages"][-1].content,
        "stage": "complete"
    }

# === Routing ===

def route_by_stage(state: MainState) -> Literal["analysis", "writing", "__end__"]:
    """Route based on current stage."""
    if state["stage"] == "analysis":
        return "analysis"
    elif state["stage"] == "writing":
        return "writing"
    return END

# === Graph Construction ===

def create_graph():
    """Build the hybrid LangGraph + Deep Agents graph."""
    builder = StateGraph(MainState)

    # Add nodes
    builder.add_node("research", research_node)
    builder.add_node("analysis", analysis_node)
    builder.add_node("writing", writing_node)

    # Define flow
    builder.add_edge(START, "research")
    builder.add_conditional_edges("research", route_by_stage)
    builder.add_conditional_edges("analysis", route_by_stage)
    builder.add_edge("writing", END)

    return builder.compile()
```

---

## 🚀 Running the Example

```bash
# Install dependencies
pip install deepagents langgraph>=0.2.0 langchain langchain-anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run
python main.py
```

---

## 🔄 Key Patterns Demonstrated

1. **State Mapping**: Converting between MainState and Deep Agent message format
2. **Sequential Pipeline**: Research → Analysis → Writing
3. **Conditional Routing**: Based on stage
4. **Clean Extraction**: Only returning summary, not full Deep Agent state

---

## 🎨 Extensions

### Add Parallel Research

```python
# Research multiple aspects in parallel
builder.add_edge(START, "research_tech")
builder.add_edge(START, "research_market")
builder.add_edge("research_tech", "combine")
builder.add_edge("research_market", "combine")
```

### Add Human Approval

```python
from langgraph.types import interrupt

def approval_node(state):
    response = interrupt({"report": state["final_report"]})
    return {"approved": response == "approve"}
```

### Add Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

---

## 💡 Key Takeaways

1. **LangGraph orchestrates**, Deep Agents execute
2. **State mapping** bridges the two systems
3. **Each Deep Agent** has its own planning, tools, context
4. **Flat structure** - no nested Deep Agents
