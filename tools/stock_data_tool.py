import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class StockDataInput(BaseModel):
    ticker: str = Field(
        ...,
        description="Stock ticker symbol to fetch data for, e.g. AAPL, MSFT, AMZN",
    )


class StockDataTool(BaseTool):
    name: str = "Stock Data Tool"
    description: str = (
        "Fetches real-time and fundamental stock data for a given ticker symbol. "
        "Returns current price, key financial ratios (P/E, EPS, debt-to-equity), "
        "market cap, revenue, margins, analyst recommendations, and recent news headlines."
    )
    args_schema: type[BaseModel] = StockDataInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info

            def fmt_currency(val):
                if isinstance(val, (int, float)):
                    if val >= 1_000_000_000:
                        return f"${val / 1_000_000_000:.2f}B"
                    if val >= 1_000_000:
                        return f"${val / 1_000_000:.2f}M"
                    return f"${val:,.2f}"
                return "N/A"

            def fmt_pct(val):
                if isinstance(val, (int, float)):
                    return f"{val * 100:.2f}%"
                return "N/A"

            def fmt_num(val, decimals=2):
                if isinstance(val, (int, float)):
                    return f"{val:.{decimals}f}"
                return "N/A"

            lines = [
                f"=== Stock Data for {ticker.upper()} ===",
                f"Company Name       : {info.get('longName', 'N/A')}",
                f"Sector / Industry  : {info.get('sector', 'N/A')} / {info.get('industry', 'N/A')}",
                "",
                "--- Price & Valuation ---",
                f"Current Price      : {fmt_currency(info.get('currentPrice') or info.get('regularMarketPrice'))}",
                f"Market Cap         : {fmt_currency(info.get('marketCap'))}",
                f"Enterprise Value   : {fmt_currency(info.get('enterpriseValue'))}",
                f"52-Week High       : {fmt_currency(info.get('fiftyTwoWeekHigh'))}",
                f"52-Week Low        : {fmt_currency(info.get('fiftyTwoWeekLow'))}",
                f"P/E Ratio (TTM)    : {fmt_num(info.get('trailingPE'))}",
                f"Forward P/E        : {fmt_num(info.get('forwardPE'))}",
                f"Price/Sales (TTM)  : {fmt_num(info.get('priceToSalesTrailing12Months'))}",
                f"Price/Book         : {fmt_num(info.get('priceToBook'))}",
                f"EV/EBITDA          : {fmt_num(info.get('enterpriseToEbitda'))}",
                "",
                "--- Financials ---",
                f"Revenue (TTM)      : {fmt_currency(info.get('totalRevenue'))}",
                f"Gross Profit       : {fmt_currency(info.get('grossProfits'))}",
                f"EBITDA             : {fmt_currency(info.get('ebitda'))}",
                f"Net Income (TTM)   : {fmt_currency(info.get('netIncomeToCommon'))}",
                f"EPS (TTM)          : {fmt_currency(info.get('trailingEps'))}",
                f"Free Cash Flow     : {fmt_currency(info.get('freeCashflow'))}",
                f"Operating Cash Flow: {fmt_currency(info.get('operatingCashflow'))}",
                "",
                "--- Margins & Returns ---",
                f"Gross Margin       : {fmt_pct(info.get('grossMargins'))}",
                f"Operating Margin   : {fmt_pct(info.get('operatingMargins'))}",
                f"Profit Margin      : {fmt_pct(info.get('profitMargins'))}",
                f"Return on Equity   : {fmt_pct(info.get('returnOnEquity'))}",
                f"Return on Assets   : {fmt_pct(info.get('returnOnAssets'))}",
                "",
                "--- Balance Sheet ---",
                f"Total Cash         : {fmt_currency(info.get('totalCash'))}",
                f"Total Debt         : {fmt_currency(info.get('totalDebt'))}",
                f"Debt/Equity Ratio  : {fmt_num(info.get('debtToEquity'))}",
                f"Current Ratio      : {fmt_num(info.get('currentRatio'))}",
                f"Quick Ratio        : {fmt_num(info.get('quickRatio'))}",
                "",
                "--- Dividends & Risk ---",
                f"Dividend Yield     : {fmt_pct(info.get('dividendYield'))}",
                f"Payout Ratio       : {fmt_pct(info.get('payoutRatio'))}",
                f"Beta               : {fmt_num(info.get('beta'))}",
                "",
                "--- Analyst Outlook ---",
                f"Recommendation     : {info.get('recommendationKey', 'N/A').upper()}",
                f"Target Mean Price  : {fmt_currency(info.get('targetMeanPrice'))}",
                f"Target Low / High  : {fmt_currency(info.get('targetLowPrice'))} / {fmt_currency(info.get('targetHighPrice'))}",
                f"Number of Analysts : {info.get('numberOfAnalystOpinions', 'N/A')}",
            ]

            summary = info.get("longBusinessSummary", "")
            if summary:
                lines += ["", "--- Business Summary ---", summary[:600] + ("..." if len(summary) > 600 else "")]

            try:
                news = stock.news
                if news:
                    lines += ["", "--- Recent News Headlines ---"]
                    for article in news[:6]:
                        title = article.get("title", "")
                        if title:
                            lines.append(f"  • {title}")
            except Exception:
                pass

            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching stock data for {ticker}: {str(e)}"
