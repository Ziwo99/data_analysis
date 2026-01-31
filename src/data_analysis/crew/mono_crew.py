"""Single-agent CrewAI pipeline for data analysis."""


from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from data_analysis.system.guardrails import mono_agent_guardrail
from data_analysis.crew.models import VisualizationsModel
from data_analysis.system.scripts import MetadataExtractor


@CrewBase
class MonoDataAnalysis:
    """Single-agent crew for complete data analysis in one pass.
    
    This crew uses one agent that performs schema interpretation,
    business analysis, query building, and visualization design
    in a single LLM call. Faster but less detailed than multi-agent.
    """

    agents_config = "config/mono_agents.yaml"
    tasks_config = "config/mono_tasks.yaml"

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def mono_agent(self) -> Agent:
        """Create the mono analysis agent."""
        return Agent(
            config=self.agents_config['mono_agent'],
            verbose=False
        )

    @task
    def mono_analysis_task(self) -> Task:
        """Create the mono analysis task."""
        return Task(
            config=self.tasks_config['mono_analysis_task'],
            output_json=VisualizationsModel,
            tools=[MetadataExtractor()],
            guardrails=[mono_agent_guardrail]
        )

    @crew
    def crew(self) -> Crew:
        """Create and return the MonoDataAnalysis crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )