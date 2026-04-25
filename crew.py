import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from tools.calculator_tool import CalculatorTool
from tools.sec_tools import SEC10KTool, SEC10QTool
from tools.stock_data_tool import StockDataTool

from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool

from dotenv import load_dotenv
load_dotenv()

# Model can be overridden via the MODEL environment variable.
# Examples:
#   MODEL=gpt-4o-mini          (OpenAI — requires OPENAI_API_KEY)
#   MODEL=ollama/llama3.1      (local Ollama — default)
#   MODEL=anthropic/claude-3-5-sonnet-20241022  (Anthropic — requires ANTHROPIC_API_KEY)
LLM_MODEL = os.environ.get("MODEL", "ollama/llama3.1")


@CrewBase
class StockAnalysisCrew:
    """Multi-agent crew for comprehensive stock / financial analysis."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------

    @agent
    def research_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_analyst"],
            verbose=True,
            llm=LLM_MODEL,
            tools=[
                ScrapeWebsiteTool(),
                WebsiteSearchTool(),
                StockDataTool(),
            ],
        )

    @agent
    def financial_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_analyst"],
            verbose=True,
            llm=LLM_MODEL,
            tools=[
                ScrapeWebsiteTool(),
                WebsiteSearchTool(),
                StockDataTool(),
                CalculatorTool(),
                SEC10QTool(),
                SEC10KTool(),
            ],
        )

    @agent
    def filing_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["filing_analyst"],
            verbose=True,
            llm=LLM_MODEL,
            tools=[
                ScrapeWebsiteTool(),
                SEC10QTool(),
                SEC10KTool(),
            ],
        )

    @agent
    def investment_advisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["investment_advisor"],
            verbose=True,
            llm=LLM_MODEL,
            tools=[
                ScrapeWebsiteTool(),
                WebsiteSearchTool(),
                StockDataTool(),
                CalculatorTool(),
            ],
        )

    # ------------------------------------------------------------------
    # Tasks  (sequential order matches the list returned by self.tasks)
    # ------------------------------------------------------------------

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config["research"],
            agent=self.research_analyst_agent(),
        )

    @task
    def financial_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["financial_analysis"],
            agent=self.financial_analyst_agent(),
        )

    @task
    def filings_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["filings_analysis"],
            agent=self.filing_analyst_agent(),
        )

    @task
    def recommend(self) -> Task:
        return Task(
            config=self.tasks_config["recommend"],
            agent=self.investment_advisor_agent(),
            output_file="output/investment_report.md",
        )

    # ------------------------------------------------------------------
    # Crew
    # ------------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Creates the Stock Analysis crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
