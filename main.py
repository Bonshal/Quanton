import sys
import os
from crew import StockAnalysisCrew


def run(company_stock: str = "AAPL") -> str:
    """Run the Stock Analysis crew for the given ticker symbol."""
    os.makedirs("output", exist_ok=True)
    inputs = {
        "company_stock": company_stock.upper(),
    }
    return StockAnalysisCrew().crew().kickoff(inputs=inputs)


def train(company_stock: str = "AAPL") -> None:
    """Train the crew for a given number of iterations (usage: train <n_iterations> [ticker])."""
    inputs = {
        "company_stock": company_stock.upper(),
    }
    try:
        n_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        StockAnalysisCrew().crew().train(n_iterations=n_iterations, inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


if __name__ == "__main__":
    # Usage: python main.py [TICKER]
    # Example: python main.py MSFT
    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"

    print("## Welcome to the Quanton Multi-Agent Financial Analyser")
    print("=" * 60)
    print(f"## Analysing: {ticker}")
    print("=" * 60)

    result = run(ticker)

    print("\n\n" + "=" * 60)
    print("## Investment Report")
    print("=" * 60)
    print(result)
    print("\nFull report saved to: output/investment_report.md")

