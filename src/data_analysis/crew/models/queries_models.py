"""Pydantic models for query builder output."""


from typing import List
from pydantic import BaseModel, Field


class QueryModel(BaseModel):
    """A sub-analysis with executable query code."""
    
    id: str = Field(description="Sub-analysis ID (e.g., 1.1, 1.2, 2.1)")
    title: str = Field(description="Title of the sub-analysis")
    why: str = Field(description="Why this sub-analysis is valuable")
    answers: List[str] = Field(description="Questions this sub-analysis answers")
    tables_columns: List[str] = Field(description="Required tables and columns")
    type: str = Field(description="Analysis type (aggregation, segmentation, etc.)")
    code_lines: List[str] = Field(description="Pandas query code lines")

class AnalysisModel(BaseModel):
    """A main analysis containing sub-analyses with queries."""
    
    id: str = Field(description="Analysis ID (e.g., 1, 2, 3)")
    title: str = Field(description="Title of the analysis")
    context: str = Field(description="Business context for this analysis")
    tables: List[str] = Field(description="Tables involved in this analysis")
    sub_analyses: List[QueryModel] = Field(
        description="Sub-analyses with query code"
    )

class QueriesModel(BaseModel):
    """Collection of all analyses with executable queries."""
    
    analyses: List[AnalysisModel] = Field(
        description="All analyses with query code"
    )
