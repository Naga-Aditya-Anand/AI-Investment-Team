from langchain_core.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY,format_ticker

client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def get_screener_fundamentals(ticker: str) -> dict:
    """Search Screener.in for detailed fundamental analysis of an Indian stock
    including valuations, financial ratios, peer comparison and historical data."""
    ticker = format_ticker(ticker).replace(".NS","").replace(".BO","")
    results = client.search(
        query=f"site:screener.in/company {ticker} fundamentals ratios",
        search_depth="advanced",
        max_results=3,
        include_answer=True,
    )

    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("url") for r in results.get("results", [])],
    }

@tool
def get_peer_comparision(ticker:str) -> dict:
    """Search for peer and competitor comparison for an Indian stock
    including sector P/E comparison and relative valuation vs industry peers."""
    ticker = format_ticker(ticker).replace(".NS", "").replace(".BO", "")
    results = client.search(
        query=f"{ticker} NSE peer comparison sector valuation competitors India",
        search_depth="advanced",
        max_results=3,
        include_answer=True,
    )

    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("url") for r in results.get("results", [])],
    }