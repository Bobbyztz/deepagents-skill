"""State Definition for Hybrid Agent

Defines the MainState TypedDict used by the LangGraph.

LangGraph Version: >=0.2.0
"""

from typing import Literal
from typing_extensions import TypedDict


class MainState(TypedDict):
    """Main state that flows through the LangGraph.
    
    Attributes:
        query: The user's original query
        research_result: Output from research Deep Agent
        analysis_result: Output from analysis Deep Agent
        final_output: The final summarized output
        stage: Current stage of processing
    """
    query: str
    research_result: str | None
    analysis_result: str | None
    final_output: str | None
    stage: Literal["research", "analysis", "complete"]
