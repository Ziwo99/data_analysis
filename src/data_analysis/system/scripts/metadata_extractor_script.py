"""Metadata extractor tool for CrewAI agents."""


from crewai.tools import BaseTool
from data_analysis.system.utils.metadata_extractor import get_raw_schema_metadata_json


class MetadataExtractor(BaseTool):
    """Tool that reads pre-extracted schema metadata from CSV files.
    
    The metadata is extracted at system startup and saved to JSON.
    This tool reads and returns that JSON to the agent for interpretation.
    """

    name: str = "MetadataExtractor"
    description: str = (
        "Read the pre-extracted raw schema metadata from the CSV database. "
        "Returns a JSON string containing tables, columns, data types, statistics, "
        "primary keys, foreign keys and relationships. "
        "Use this metadata to interpret and describe the database structure."
    )

    def _run(self) -> str:
        """Read and return the pre-extracted schema metadata.
        
        Returns:
            JSON string containing raw schema metadata.
        """
        return get_raw_schema_metadata_json()

