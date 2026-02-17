"""
Vision Analysis Crew — CrewAI-based agent for car image analysis.

This crew wraps the vision analysis capability as a proper AI agent,
following the same pattern as the car chat crew.
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from ai_engine.tools import gemini_vision_llm


@CrewBase
class VisionAnalysisCrew:
    """Crew for analyzing car images and extracting structured data."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def vision_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['vision_analyst'],
            verbose=True,
            llm=gemini_vision_llm,
        )

    @task
    def vision_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['vision_analysis_task'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
