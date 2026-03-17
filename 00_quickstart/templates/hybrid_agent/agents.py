"""Deep Agent Definitions for Hybrid Template

Defines specialized Deep Agents that will be used as LangGraph nodes.

LangGraph Version: >=0.2.0
"""

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from deepagents import create_deep_agent

# ============================================================================
# Configuration
# ============================================================================

MODEL = "anthropic:claude-sonnet-4-5-20250929"
TEMPERATURE = 0.0

model = init_chat_model(MODEL, temperature=TEMPERATURE)

# ============================================================================
# Tools
# ============================================================================

@tool
def web_search(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: The search query
        
    Returns:
        Search results
    """
    # TODO: Replace with actual search implementation
    return f"Search results for '{query}': [placeholder - implement actual search]"


@tool
def think_tool(reflection: str) -> str:
    """Reflect on current findings and plan next steps.
    
    Args:
        reflection: Your thoughts on what you've found and what to do next
        
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
    # TODO: Replace with actual analysis implementation
    return f"Analysis of provided data: [placeholder - implement actual analysis]"


# ============================================================================
# Research Agent
# ============================================================================

RESEARCH_PROMPT = """You are a research specialist.

## Your Task
Conduct thorough research on the given topic.

## Instructions
1. Use web_search to find relevant information
2. Use think_tool to reflect on findings
3. Return a comprehensive summary with sources

## Output Format
Provide findings with inline citations [1], [2], etc.
"""

research_agent = create_deep_agent(
    model=model,
    tools=[web_search, think_tool],
    system_prompt=RESEARCH_PROMPT
)

# ============================================================================
# Analysis Agent
# ============================================================================

ANALYSIS_PROMPT = """You are an analysis specialist.

## Your Task
Analyze the provided information and extract insights.

## Instructions
1. Review the input carefully
2. Identify key patterns and insights
3. Use analyze_data tool for structured analysis
4. Provide actionable recommendations

## Output Format
Structure your analysis with:
- Key Findings
- Insights
- Recommendations
"""

analysis_agent = create_deep_agent(
    model=model,
    tools=[analyze_data, think_tool],
    system_prompt=ANALYSIS_PROMPT
)
