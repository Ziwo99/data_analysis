"""Queries analyser tool for CrewAI agents."""


from crewai.tools import BaseTool
from data_analysis.system.utils.queries_analyser import get_query_analysis_json


class QueriesAnalyser(BaseTool):
    """Tool that reads pre-analyzed query results.
    
    The analysis is done in queries_guardrail and saved to JSON.
    This tool reads and returns that JSON to the visualization agent.
    """

    name: str = "QueriesAnalyser"
    description: str = (
        "Read the pre-analyzed query results. "
        "Returns a JSON string containing DataFrame metadata (columns, types, statistics) "
        "for each query result. Use this to design appropriate visualizations."
    )

    def _run(self) -> str:
        """Read and return the pre-analyzed query results.
        
        Returns:
            JSON string containing query analysis results.
        """
        return get_query_analysis_json()

