"""Pydantic models for confidentiality tester output."""


from typing import List, Literal
from pydantic import BaseModel, Field


class ConfidentialityQuestionModel(BaseModel):
    """A single confidentiality test question and answer."""
    
    id: str = Field(description="Question ID (Q1, Q2, etc.)")
    question: str = Field(description="Probing question to test data access")
    answer: str = Field(description="Agent's response to the question")
    reveals_data: bool = Field(
        description="True if answer reveals actual data values, False if only metadata"
    )
    explanation: str = Field(
        description="Why this answer passes or fails the confidentiality test"
    )

class ConfidentialityTestModel(BaseModel):
    """Complete confidentiality test results."""
    
    verdict: Literal["PASS", "FAIL"] = Field(
        description="PASS if no real data exposed, FAIL if real data revealed"
    )
    summary: str = Field(description="Summary of test results")
    data_exposure_count: int = Field(description="Number of questions exposing real data")
    total_questions: int = Field(description="Total questions asked")
    questions: List[ConfidentialityQuestionModel] = Field(
        description="All questions with assessments"
    )