"""Multi-agent CrewAI pipeline for data analysis."""


from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from data_analysis.system.guardrails import (
    queries_guardrail,
    analysis_guardrail,
    confidentiality_guardrail,
    metadata_guardrail,
    visualization_guardrail,
)
from data_analysis.crew.models import (
    QueriesModel,
    BusinessAnalysisModel,
    ConfidentialityTestModel,
    EnrichedMetadataModel,
    VisualizationsModel,
)
from data_analysis.system.scripts import MetadataExtractor, QueriesAnalyser


@CrewBase
class DataAnalysis:
    """Multi-agent crew for sequential data analysis.
    
    This crew orchestrates 5 specialized agents:
    1. Schema Interpreter - Analyzes database schema
    2. Business Analyst - Identifies analytical opportunities
    3. Query Builder - Generates Pandas queries
    4. Visualization Designer - Creates matplotlib visualizations
    5. Confidentiality Tester - Audits data access
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def schema_interpreter(self) -> Agent:
        """Create the schema interpreter agent."""
        return Agent(
            config=self.agents_config['schema_interpreter'],
            verbose=False
        )

    @agent
    def business_analyst(self) -> Agent:
        """Create the business analyst agent."""
        return Agent(
            config=self.agents_config['business_analyst'],
            verbose=False
        )

    @agent
    def query_builder(self) -> Agent:
        """Create the query builder agent."""
        return Agent(
            config=self.agents_config['query_builder'],
            verbose=False
        )

    @agent
    def visualization_designer(self) -> Agent:
        """Create the visualization designer agent."""
        return Agent(
            config=self.agents_config['visualization_designer'],
            verbose=False
        )

    @agent
    def confidentiality_tester(self) -> Agent:
        """Create the confidentiality tester agent."""
        return Agent(
            config=self.agents_config['confidentiality_tester'],
            verbose=False
        )

    @task
    def interpret_schema_task(self) -> Task:
        """Create the schema interpretation task."""
        return Task(
            config=self.tasks_config['interpret_schema_task'],
            output_json=EnrichedMetadataModel,
            tools=[MetadataExtractor()],
            guardrails=[metadata_guardrail]
        )

    @task
    def business_analysis_task(self) -> Task:
        """Create the business analysis task."""
        return Task(
            config=self.tasks_config['business_analysis_task'],
            output_json=BusinessAnalysisModel,
            guardrails=[analysis_guardrail]
        )

    @task
    def build_query_task(self) -> Task:
        """Create the query building task."""
        return Task(
            config=self.tasks_config['build_query_task'],
            output_json=QueriesModel,
            guardrails=[queries_guardrail]
        )

    @task
    def design_visualization_task(self) -> Task:
        """Create the visualization design task."""
        return Task(
            config=self.tasks_config['design_visualization_task'],
            output_json=VisualizationsModel,
            tools=[QueriesAnalyser()],
            guardrails=[visualization_guardrail]
        )

    @task
    def confidentiality_test_task(self) -> Task:
        """Create the confidentiality testing task."""
        return Task(
            config=self.tasks_config['confidentiality_test_task'],
            output_json=ConfidentialityTestModel,
            guardrails=[confidentiality_guardrail]
        )

    @crew
    def crew(self) -> Crew:
        """Create and return the DataAnalysis crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )