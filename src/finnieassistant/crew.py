from typing import List
import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from finnieassistant.tools.custom_tool import YahooFinanceTool, TavilySearchTool, PortfolioAnalysisTool
from pprint import pprint
from dotenv import load_dotenv

# Load .env file into environment
load_dotenv()

@CrewBase
class Finnieassistant:
    """Finnieassistant Crew with manager-led dynamic task selection"""

    agents: List[BaseAgent]
    tasks: List[Task]


    # -----------------------------
    # LLM (lazy-safe)
    # -----------------------------
    def _llm(self) -> LLM:
        return LLM(
            model=os.getenv("OPENROUTER_MODEL_NAME"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            temperature=0.2,
            verbose=True,
        )

    # -----------------------------
    # TOOLS (single instances)
    # -----------------------------
    yahoo_tool = YahooFinanceTool()
    tavily_tool = TavilySearchTool()
    portfolio_tool = PortfolioAnalysisTool()

    # --------------------------------------------------
    # AGENTS (from agents.yaml)
    # --------------------------------------------------
    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            llm=self._llm(),
            config=self.agents_config["planner_agent"],  # type: ignore[index]
            verbose=True,
        )
    @agent
    def finance_guru(self) -> Agent:
        return Agent(
            llm=self._llm(),
            config=self.agents_config["finance_guru"],  # type: ignore[index]
            tools=[self.yahoo_tool, self.tavily_tool],
            verbose=True,
        )

    @agent
    def portfolio_analyst(self) -> Agent:
        return Agent(
            llm=self._llm(),
            config=self.agents_config["portfolio_analyst"],  # type: ignore[index]
            tools=[self.portfolio_tool, self.yahoo_tool, self.tavily_tool],
            verbose=True,
        )

    @agent
    def learning_coach(self) -> Agent:
        return Agent(
            llm=self._llm(),
            config=self.agents_config["learning_coach"],  # type: ignore[index]
            verbose=True,
        )

    # --------------------------------------------------
    # TASKS (ALL DEFINED, NONE FORCED)
    # --------------------------------------------------
    @task
    def coordinate_request(self) -> Task:
        return Task(
            config=self.tasks_config["coordinate_request"],  # type: ignore[index]
            agent=self.planner_agent(),
        )

    @task
    def analyze_stock(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_stock"],  # type: ignore[index]
            agent=self.finance_guru(),
        )

    @task
    def analyze_portfolio(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_portfolio"],  # type: ignore[index]
            agent=self.portfolio_analyst(),
        )

    @task
    def teach_concept(self) -> Task:
        return Task(
            config=self.tasks_config["teach_concept"],  # type: ignore[index]
            agent=self.learning_coach(),
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------

    @crew
    def stock_crew(self) -> Crew:
        return Crew(
            agents=[self.finance_guru()],  # Added brackets
            tasks=[self.analyze_stock()],   # Added brackets
            verbose=True,
        )

    @crew
    def portfolio_crew(self) -> Crew:
        return Crew(
            agents=[self.portfolio_analyst()], # Added brackets
            tasks=[self.analyze_portfolio()],   # Added brackets
            verbose=True,
        )

    @crew
    def coach_crew(self) -> Crew:
        return Crew(
            agents=[self.learning_coach()], # Added brackets
            tasks=[self.teach_concept()],   # Added brackets
            verbose=True,
        )

    @crew
    def planner_crew(self) -> Crew:
        return Crew(
            agents=[self.planner_agent()], # Added brackets
            tasks=[self.coordinate_request()], # Added brackets
            verbose=True,
        )

    #custom function
    def run_finnie(self, user_query):
        # 1. Ask the Planner to categorize
        result = self.planner_crew().kickoff(inputs={'query': user_query})

        # If it's a CrewOutput object, get the raw string
        category = result.raw

        # 2. Run ONLY the relevant crew/task
        if "STOCK" in category:
            return self.stock_crew().kickoff(inputs={'query': user_query})
        elif "PORTFOLIO" in category:
            return self.portfolio_crew().kickoff(inputs={'query': user_query})
        elif "COACH" in category:
            return self.coach_crew().kickoff(inputs={'query': user_query})
        else:
            return "I need a bit more detail! Would you like to analyze a stock or learn a concept?"