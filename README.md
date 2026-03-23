# Quanton – AI-Powered Stock Analysis

Quanton is a multi-agent AI system that researches a publicly-traded company and produces a detailed investment recommendation. It is built on the [CrewAI](https://github.com/joaomdmoura/crewAI) framework and runs all LLM inference locally through [Ollama](https://ollama.com/).

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Key Technologies](#key-technologies)
- [Agents and Tasks](#agents-and-tasks)
- [Tools](#tools)
- [Configuration](#configuration)
- [Setup and Usage](#setup-and-usage)
- [Environment Variables](#environment-variables)

---

## Overview

Given a stock ticker (e.g. `AMZN`), the system spins up three specialised AI agents that work sequentially:

1. **Financial Analyst** – examines key financial metrics and compares the stock to its peers.
2. **Research Analyst** – collects and summarises recent news, press releases, and market sentiment.
3. **Investment Advisor** – synthesises the outputs from the other two agents and produces a final, formatted investment recommendation.

---

## Repository Structure

```
Quanton/
├── __init__.py               # Package marker
├── main.py                   # Entry point: run() and train() helpers
├── crew.py                   # CrewAI crew definition (agents + tasks)
├── pyproject.toml            # Project metadata and dependencies (uv / pip)
├── uv.lock                   # Locked dependency versions
├── config/
│   ├── agents.yaml           # Role, goal, and backstory for each agent
│   └── tasks.yaml            # Description and expected output for each task
└── tools/
    ├── __init__.py           # Package marker
    ├── calculator_tool.py    # Safe arithmetic expression evaluator
    └── sec_tools.py          # RAG tools for fetching SEC 10-K / 10-Q filings
```

### `main.py`

The application entry point. Defines two functions:

| Function | Purpose |
|----------|---------|
| `run()` | Kicks off a single analysis run for a given `company_stock` ticker. |
| `train(n)` | Runs `n` training iterations to improve crew behaviour over time. |

### `crew.py`

Defines the `StockAnalysisCrew` class using the `@CrewBase` decorator. The class wires together agents and tasks and exposes a `crew()` method that returns a sequential `Crew` object ready to be kicked off.

### `config/agents.yaml`

Declarative configuration for every agent: their **role**, **goal**, and **backstory**. CrewAI injects these strings directly into the system prompt.

### `config/tasks.yaml`

Declarative configuration for every task: a **description** (the actual instruction given to the agent) and an **expected_output** (the acceptance criteria for the agent's response). Task descriptions support `{variable}` placeholders that are filled at runtime (e.g. `{company_stock}`).

### `tools/`

Custom tools that extend the agents' capabilities beyond what is available out of the box.

---

## Key Technologies

| Technology | Role |
|------------|------|
| [CrewAI](https://github.com/joaomdmoura/crewAI) | Multi-agent orchestration framework |
| [LangChain + Ollama](https://python.langchain.com/docs/integrations/llms/ollama) | Local LLM inference (`llama3.1`) |
| [crewai-tools](https://github.com/joaomdmoura/crewAI-tools) | Pre-built tools (web scraping, RAG, etc.) |
| [SEC API](https://sec-api.io/) | Programmatic access to SEC EDGAR filings |
| [embedchain](https://github.com/embedchain/embedchain) | Vector-store backend used by the RAG tools |
| [html2text](https://github.com/Alir3z4/html2text) | Converts raw HTML from SEC filings to plain text |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Loads secrets from a `.env` file at startup |
| [uv](https://github.com/astral-sh/uv) | Fast Python package manager / lock file |

---

## Agents and Tasks

### Agents (`config/agents.yaml`)

| Agent key | Role | Responsibilities |
|-----------|------|-----------------|
| `financial_analyst` | The Best Financial Analyst | Analyse financial metrics, compare peers, scrape web data, and read SEC filings |
| `research_analyst` | Staff Research Analyst | Gather news, press releases, and market sentiment; read SEC filings |
| `investment_advisor` | Private Investment Advisor | Synthesise all analyses into a final investment recommendation |

### Tasks (`config/tasks.yaml`)

Tasks execute **sequentially** in the following order:

1. **`financial_analysis`** – Examines P/E ratio, EPS growth, revenue trends, and debt-to-equity ratio for `{company_stock}`. Assigned to `financial_analyst_agent`.
2. **`research`** – Collects recent news and market analyses, including upcoming earnings events. Assigned to `research_analyst_agent`.
3. **`filings_analysis`** – Parses the latest 10-Q and 10-K from EDGAR; extracts risks, insider trading activity, and management discussion highlights. Assigned to `financial_analyst_agent`.
4. **`recommend`** – Combines all prior outputs into a detailed, well-formatted investment recommendation. Assigned to `investment_advisor_agent`.

---

## Tools

### `CalculatorTool` (`tools/calculator_tool.py`)

A safe arithmetic evaluator that accepts a mathematical expression string (e.g. `200*7` or `5000/2*10`) and returns the numeric result. It parses the expression into an AST and evaluates only a whitelisted set of operators, preventing code injection.

### `SEC10KTool` / `SEC10QTool` (`tools/sec_tools.py`)

RAG (Retrieval-Augmented Generation) tools built on top of `crewai_tools.RagTool`:

- On initialisation, they query the SEC EDGAR API for the most recent **10-K** (annual) or **10-Q** (quarterly) filing for a given ticker.
- The HTML filing is fetched, converted to plain text, and indexed in an embedchain vector store.
- At runtime, the agent passes a natural-language query and the tool returns semantically relevant excerpts from the filing.
- When a `stock_name` is provided at construction time, the schema is simplified so the agent only needs to supply a `search_query`.

### Third-party tools (from `crewai_tools`)

| Tool | Used by |
|------|---------|
| `ScrapeWebsiteTool` | All three agents – extracts content from a given URL |
| `WebsiteSearchTool` | `financial_analyst_agent`, `investment_advisor_agent` – semantic search across a website |

---

## Configuration

### `pyproject.toml`

Defines the Python package `stock_analysis` and two CLI entry points:

```
stock_analysis   →  stock_analysis.main:run
train            →  stock_analysis.main:train
```

Requires **Python 3.12 – 3.13**.

### LLM

The LLM is configured at the top of `crew.py`:

```python
from langchain.llms import Ollama
llm = Ollama(model="llama3.1")
```

To switch models, change the `model` argument to any model available in your local Ollama installation.

---

## Setup and Usage

### Prerequisites

- [Ollama](https://ollama.com/) installed and running with the `llama3.1` model pulled:
  ```bash
  ollama pull llama3.1
  ```
- A [SEC API](https://sec-api.io/) key.

### Install dependencies

```bash
pip install uv          # if not already installed
uv sync                 # installs all locked dependencies from uv.lock
```

### Create a `.env` file

```
SEC_API_API_KEY=your_sec_api_key_here
```

### Run the analysis

```bash
python main.py
```

The default ticker is `AMZN`. To analyse a different company, edit the `company_stock` value in `main.py`:

```python
inputs = {
    'query': 'What is the company you want to analyze?',
    'company_stock': 'TSLA',   # ← change this
}
```

### Train the crew

```bash
python -c "import sys; sys.argv = ['', '5']; from main import train; train()"
# or, after installing as a package:
train 5
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEC_API_API_KEY` | Yes | API key for [sec-api.io](https://sec-api.io/) used to query SEC EDGAR filings |
