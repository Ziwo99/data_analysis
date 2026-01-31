"""Pydantic models for visualization designer output."""


from typing import List
from pydantic import BaseModel, Field


class VisualizationQueryModel(BaseModel):
    """A sub-analysis with query and visualization code."""
    
    id: str = Field(description="Sub-analysis ID (e.g., 1.1, 1.2, 2.1)")
    title: str = Field(description="Title of the sub-analysis")
    why: str = Field(description="Why this sub-analysis is valuable")
    answers: List[str] = Field(description="Questions this sub-analysis answers")
    tables_columns: List[str] = Field(description="Required tables and columns")
    type: str = Field(description="Analysis type (aggregation, segmentation, etc.)")
    code_lines: List[str] = Field(description="Pandas query code lines")
    visualization_code: List[str] = Field(description="Matplotlib visualization code")
    visualization_type: str = Field(description="Chart type (bar, line, pie, etc.)")
    justification: str = Field(description="Why this chart type was chosen")

class VisualizationAnalysisModel(BaseModel):
    """A main analysis containing sub-analyses with visualizations."""
    
    id: str = Field(description="Analysis ID (e.g., 1, 2, 3)")
    title: str = Field(description="Title of the analysis")
    context: str = Field(description="Business context for this analysis")
    tables: List[str] = Field(description="Tables involved in this analysis")
    sub_analyses: List[VisualizationQueryModel] = Field(
        description="Sub-analyses with visualization code"
    )

class VisualizationsModel(BaseModel):
    """Collection of all analyses with visualizations."""
    
    analyses: List[VisualizationAnalysisModel] = Field(
        description="All analyses with visualization code"
    )
