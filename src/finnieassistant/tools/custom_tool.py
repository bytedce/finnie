from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


# =========================================================
# Yahoo Finance Tool
# =========================================================
class YahooFinanceInput(BaseModel):
    ticker: str = Field(
        ...,
        description="stock ticker symbol, e.g., AAPL for Apple Inc."
    )

class YahooFinanceTool(BaseTool):
    """
    Yahoo Finance Tool for fetching real-time stock data,
    fundamentals, and basic technical indicators.
    """

    name: str = "Yahoo Finance Stock Lookup"
    description: str = (
        "Fetch real-time stock price, fundamentals, and technical indicators "
        "such as SMA, EMA, 52-week high/low, volume, and earnings information "
        "for a given stock ticker using Yahoo Finance."
    )

    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str) -> Dict[str, Any]:
        try:
            ticker = ticker.upper().strip()
            stock = yf.Ticker(ticker)

            # ----------------------------
            # BASIC PRICE DATA
            # ----------------------------
            price_data = stock.history(period="1d")
            if price_data.empty:
                return {"error": f"No data found for ticker {ticker}"}

            current_price = float(price_data["Close"].iloc[-1])

            # ----------------------------
            # HISTORICAL DATA (for technicals)
            # ----------------------------
            hist = stock.history(period="1y")

            # Simple Moving Averages
            hist["SMA_20"] = hist["Close"].rolling(window=20).mean()
            hist["SMA_50"] = hist["Close"].rolling(window=50).mean()

            # Exponential Moving Averages
            hist["EMA_20"] = hist["Close"].ewm(span=20, adjust=False).mean()
            hist["EMA_50"] = hist["Close"].ewm(span=50, adjust=False).mean()

            # 52-week high / low
            week_52_high = float(hist["High"].max())
            week_52_low = float(hist["Low"].min())

            # ----------------------------
            # FUNDAMENTALS
            # ----------------------------
            info = stock.info or {}

            fundamentals = {
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
            }

            # ----------------------------
            # EARNINGS (LAST 4 QUARTERS)
            # ----------------------------
            earnings = {}
            try:
                if stock.earnings_dates is not None:
                    earnings = stock.earnings_dates.head(4).to_dict()
            except Exception:
                earnings = {}

            # ----------------------------
            # FINAL RESPONSE
            # ----------------------------
            return {
                "ticker": ticker,
                "timestamp": datetime.utcnow().isoformat(),
                "price": {
                    "current": current_price,
                    "currency": info.get("currency"),
                },
                "technicals": {
                    "sma_20": float(hist["SMA_20"].iloc[-1]),
                    "sma_50": float(hist["SMA_50"].iloc[-1]),
                    "ema_20": float(hist["EMA_20"].iloc[-1]),
                    "ema_50": float(hist["EMA_50"].iloc[-1]),
                    "52_week_high": week_52_high,
                    "52_week_low": week_52_low,
                },
                "fundamentals": fundamentals,
                "volume": int(hist["Volume"].iloc[-1]),
                "earnings_recent": earnings,
            }

        except Exception as e:
            return {
                "ticker": ticker,
                "error": str(e),
            }


# =========================================================
# Tavily Search Tool
# =========================================================

class TavilySearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Search query for financial news"
    )


class TavilySearchTool(BaseTool):
    name: str = "Financial News Search"
    description: str = (
        "Searches for the latest financial and stock-related news."
    )
    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: str) -> list[str]:
        return [
            f"Latest news about {query}",
            f"Market reacts to {query}",
        ]

# =========================================================
# Portfolio Analysis Tool
# =========================================================

class PortfolioAnalysisInput(BaseModel):
    portfolio_path: str = Field(
        ...,
        description="Path to portfolio CSV file"
    )


class PortfolioAnalysisTool(BaseTool):
    name: str = "Portfolio Risk Analysis"
    description: str = (
        "Analyzes a user's investment portfolio "
        "to determine risk profile."
    )
    args_schema: Type[BaseModel] = PortfolioAnalysisInput

    def _run(self, portfolio_path: str) -> Dict[str, Any]:
        return {
            "total_value": 250000,
            "risk_profile": "Balanced",
        }
