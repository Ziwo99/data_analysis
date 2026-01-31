"""Pydantic models for business analysis output."""


from typing import List
from pydantic import BaseModel, Field


class BusinessSubAnalysisModel(BaseModel):
    """A single sub-analysis within a business analysis."""
    
    id: str = Field(description="Sub-analysis ID (e.g., 1.1, 1.2, 2.1)")
    title: str = Field(description="Title of the sub-analysis")
    why: str = Field(description="Why this sub-analysis is valuable")
    answers: List[str] = Field(description="Questions this sub-analysis answers")
    tables_columns: List[str] = Field(description="Required tables and columns")

class BusinessAnalysisItemModel(BaseModel):
    """A main analysis containing multiple sub-analyses."""
    
    id: str = Field(description="Analysis ID (e.g., 1, 2, 3)")
    title: str = Field(description="Title of the analysis")
    context: str = Field(description="Business context for this analysis")
    tables: List[str] = Field(description="Tables involved in this analysis")
    sub_analyses: List[BusinessSubAnalysisModel] = Field(
        description="Sub-analyses for this analysis"
    )

class BusinessAnalysisModel(BaseModel):
    """Collection of all business analyses."""
    
    analyses: List[BusinessAnalysisItemModel] = Field(
        description="All planned analyses"
    )