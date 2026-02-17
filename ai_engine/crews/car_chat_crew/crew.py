"""
Car Chat Crew — CrewAI-based conversational agent for IntelliWheels.

Follows the course pattern (agents_htu) with YAML config for agents and tasks,
and a dedicated LLM instance from ai_engine.tools.
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from ai_engine.tools import gemini_llm


@CrewBase
class CarChatCrew:
    """Crew for handling car-related chat conversations."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def car_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['car_advisor'],
            verbose=True,
            llm=gemini_llm,
        )

    @task
    def car_advisor_task(self) -> Task:
        return Task(
            config=self.tasks_config['car_advisor_task'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
