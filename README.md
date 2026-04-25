# Quanton — Multi-Agent Financial Analyser

> A production-ready, multi-agent financial analysis system built with [CrewAI](https://crewai.com).  
> Given any stock ticker, four specialised AI agents collaborate sequentially to produce a comprehensive investment report.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     StockAnalysisCrew                           │
│                                                                 │
│  ① Research Analyst ──► Market Research Report                 │
│        │                                                        │
│        ▼                                                        │
│  ② Financial Analyst ──► Financial Analysis Report             │
│        │                                                        │
│        ▼                                                        │
│  ③ Filing Analyst ──► SEC Filings Report                       │
│        │                                                        │
│        ▼                                                        │
│  ④ Investment Advisor ──► Final Investment Recommendation       │
└─────────────────────────────────────────────────────────────────┘
```

### Agents

| # | Agent | Responsibility |
|---|-------|----------------|
| 1 | **Research Analyst** | News, market sentiment, analyst ratings, upcoming catalysts |
| 2 | **Financial Analyst** | Valuation ratios, growth, margins, cash flow, peer benchmarking |
| 3 | **Filing Analyst** | SEC 10-K / 10-Q — MD&A, risk factors, insider trading, red flags |
| 4 | **Investment Advisor** | Synthesises all reports → Buy/Hold/Sell + price target |

### Tools

| Tool | Purpose |
|------|---------|
| `StockDataTool` | Live stock price, valuation ratios, financials (via `yfinance`) |
| `SEC10KTool` | Semantic search over the latest 10-K annual filing |
| `SEC10QTool` | Semantic search over the latest 10-Q quarterly filing |
| `CalculatorTool` | Safe arithmetic for derived financial metrics |
| `ScrapeWebsiteTool` | Scrape web pages for research |
| `WebsiteSearchTool` | RAG-enhanced search over web content |

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/Bonshal/Quanton.git
cd Quanton
```

### 2. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Required keys:
- **`OPENAI_API_KEY`** — or set `MODEL=ollama/llama3.1` for a free local model
- **`SEC_API_API_KEY`** — free at [sec-api.io](https://sec-api.io) (needed for 10-K/10-Q tools)

Optional:
- **`SERPER_API_KEY`** — improves web search quality

### 4. Run an analysis

```bash
# Analyse Apple (default)
python main.py AAPL

# Analyse any ticker
python main.py MSFT
python main.py NVDA
python main.py TSLA
```

The final investment report is saved to `output/investment_report.md` and also printed to the console.

---

## Using a Local Model (Ollama)

No API key required — run entirely on your machine:

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.1

# Set the model in .env
echo "MODEL=ollama/llama3.1" >> .env

python main.py AAPL
```

> **Note:** Local models produce lower-quality analysis than GPT-4o or Claude.  
> `llama3.1` (8B) is a reasonable free baseline.

---

## Output

The final report (`output/investment_report.md`) contains:

- **Executive Summary**
- **Investment Stance & 12-Month Price Target** (Bull / Base / Bear)
- **Key Investment Thesis** (top 3 reasons)
- **Key Risks** (top 3)
- **Financial Highlights** (valuation table, margins, cash flow)
- **Market Sentiment & News Catalysts**
- **SEC Filings Insights** (insider trades, red flags)
- **Portfolio Positioning Suggestion**
- **Conclusion**

---

## Project Structure

```
Quanton/
├── main.py               # Entry point — accepts ticker as CLI arg
├── crew.py               # CrewAI crew definition (agents + tasks)
├── config/
│   ├── agents.yaml       # Agent roles, goals, and backstories
│   └── tasks.yaml        # Task descriptions and expected outputs
├── tools/
│   ├── stock_data_tool.py  # Real-time stock data via yfinance
│   ├── sec_tools.py        # SEC 10-K / 10-Q RAG tools
│   └── calculator_tool.py  # Safe mathematical expression evaluator
├── output/               # Generated reports (git-ignored)
├── .env.example          # Environment variable template
└── pyproject.toml        # Project metadata and dependencies
```

---

## Training the Crew

CrewAI supports iterative crew training to improve agent outputs:

```bash
python -c "from main import train; train('AAPL')" 5
```

---

## License

MIT
