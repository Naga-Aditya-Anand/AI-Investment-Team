from langchain_core.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY,format_ticker

client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def search_stock_news(ticker: str) -> dict:
    """Search for the latest news, earnings updates, management commentary
    and corporate announcements for an Indian NSE listed stock.
    Use This tool Only ONCE, Do NOT call the Tool again once the tool returns the status as success."""

    ticker_clean = format_ticker(ticker).replace(".NS", "").replace(".BO", "")
    results = client.search(
        query=f"{ticker_clean} NSE stock news earnings results announcement",
        search_depth="advanced",
        max_results=5,
        include_answer=True,
    )

    articles = []
    for r in results.get("results",[]):
        articles.append({
            "title": r.get("title"),
            "summary": r.get("content", "")[:300],
            "url": r.get("url"),
            "published_date": r.get("published_date"),
        })

    return {
        "summary": results.get("answer", ""),
        "articles": articles,
        "status":"success",
    }


@tool
def search_analyst_ratings(ticker: str) -> dict:
    """Search for analyst ratings, price targets and buy/sell/hold recommendations
    for an Indian stock from brokerages like Motilal Oswal, Kotak, ICICI Securities.
    Use This tool Only ONCE, Do NOT call the Tool again once the tool returns the status as success."""

    ticker_clean = format_ticker(ticker).replace(".NS", "").replace(".BO", "")
    results = client.search(
        query=f"{ticker_clean} analyst rating price target buy sell hold NSE 2026",
        search_depth="advanced",
        max_results=4,
        include_answer=True,
    )
    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("title") for r in results.get("results", [])],
        "status":"success",
    }

@tool
def search_india_marco_news() -> dict:
    """Search for latest Indian macroeconomic news including RBI monetary policy,
    repo rate decisions, India inflation, GDP growth and FII/DII activity.
    Use This tool Only ONCE, Do NOT call the Tool again once the tool returns the status as success."""

    results = client.search(
        query="India RBI repo rate inflation GDP FII DII stock market 2026",
        search_depth="advanced",
        max_results=4,
        include_answer=True,
    )

    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("title") for r in results.get("results", [])],
        "status":"success",
    }


@tool
def search_sector_outlook(sector: str) -> dict:
    """Search for the current outlook, trends and challenges for a specific
    sector in the Indian stock market such as IT, banking, pharma, FMCG, auto.
    Use This tool Only ONCE, Do NOT call the Tool again once the tool returns the status as success."""

    results = client.search(
        query=f"{sector} sector India stock market outlook 2025 NSE",
        search_depth="advanced",
        max_results=3,
        include_answer=True,
    )
    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("title") for r in results.get("results", [])],
        "status":"success",
    }


@tool
def search_bse_filings(ticker: str) -> dict:
    """Search for recent BSE/NSE regulatory filings, shareholding patterns,
    insider trading disclosures and quarterly result filings for an Indian stock.
    Use This tool Only ONCE, Do NOT call the Tool again once the tool returns the status as success."""

    ticker_clean = format_ticker(ticker).replace(".NS", "").replace(".BO", "")
    results = client.search(
        query=f"{ticker_clean} BSE NSE filing shareholding quarterly results disclosure",
        search_depth="basic",
        max_results=3,
        include_answer=True,
    )
    return {
        "summary": results.get("answer", ""),
        "sources": [r.get("title") for r in results.get("results", [])],
        "status":"success",
    }