import yfinance as yf
import pandas as pd
import ta
from langchain_core.tools import tool
from config import format_ticker

@tool
def get_company_profile(ticker:str) -> dict:
    """Get Indian stock company profile including sector, industry, market cap,
    beta, 52 week high/low and company description for NSE listed stocks."""

    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    info = stock.info

    if not info:
        return {"error": f"No data found for {ticker}"}
    return{
        "ticker": ticker,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
        "description": info.get("longBusinessSummary", "")[:500],
        "exchange": info.get("exchange"),
        "currency": info.get("currency"),
    }

@tool
def get_fundamental_data(ticker:str) -> dict:
    """Get fundamental financial data for an Indian NSE stock including
    P/E ratio, EPS, revenue, profit margins, ROE, debt to equity and dividend yield."""
    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    info = stock.info
    if not info:
        return {"error": f"No fundamental data for {ticker}"}
    return {
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        "eps": info.get("trailingEps"),
        "forward_eps": info.get("forwardEps"),
        "revenue": info.get("totalRevenue"),
        "profit_margin": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        "earnings_growth": info.get("earningsGrowth"),
        "revenue_growth": info.get("revenueGrowth"),
    }


@tool
def get_income_statement(ticker: str) -> dict:
    """Get the annual income statement for an Indian NSE stock showing
    revenue, gross profit, operating income, net income and EBITDA for last 2 years."""
    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    financials = stock.financials
    if financials is None or financials.empty:
        return {"error": f"No income statement for {ticker}"}
    results = []
    for col in financials.columns[:2]:
        year_data = financials[col]
        results.append({
            "year": str(col.year),
            "revenue": year_data.get("Total Revenue"),
            "gross_profit": year_data.get("Gross Profit"),
            "operating_income": year_data.get("Operating Income"),
            "net_income": year_data.get("Net Income"),
            "ebitda": year_data.get("EBITDA"),
        })
    
    return {"income_statements": results}


@tool
def get_balance_sheet(ticker:str) -> dict:
    """Get the latest balance sheet for an Indian NSE stock including
    total assets, total debt, cash, equity and debt to equity ratio."""

    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    bs = stock.balance_sheet.fillna(0)
    
    if bs is None or bs.empty:
        return {"error": f"No balance sheet for {ticker}"}
    
    latest = bs.iloc[:,0]
    total_debt = latest.get("Total Debt",0) or 0
    total_equity = latest.get("Stockholders Equity", 1) or 1

    return {
        "total_assets": latest.get("Total Assets"),
        "total_debt": total_debt,
        "cash": latest.get("Cash And Cash Equivalents"),
        "total_equity": total_equity,
        "debt_to_equity": round(total_debt / total_equity, 2),
    }


@tool
def get_current_price(ticker: str) -> dict:
    """Get the current market price and today's trading data for an Indian NSE stock
    including open, high, low, close, volume and previous close."""
    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    info = stock.info
    return{
        "ticker": ticker,
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "open": info.get("open"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "volume": info.get("volume"),
        "avg_volume": info.get("averageVolume"),
    }


@tool
def get_technical_indicators(ticker: str) -> dict:
    """Get technical analysis indicators for an Indian NSE stock including
    RSI, MACD, Bollinger Bands, Moving Averages (50, 200) and ATR volatility."""

    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")

    if df.empty:
        return {"error": f"No price history for {ticker}"}
    
    close = df["Close"]
    current_price = close.iloc[-1]

    # Moving Averages
    ma_50 = close.rolling(window=50).mean().iloc[-1]
    ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None

    # RSI
    rsi = ta.momentum.RSIIndicator(close=close,window=14).rsi().iloc[-1]

    # MACD
    macd_ind = ta.trend.MACD(close=close)
    macd = macd_ind.macd().iloc[-1]
    macd_signal = macd_ind.macd_signal().iloc[-1]

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close=close, window=20)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    # ATR
    atr = ta.volatility.AverageTrueRange(
        high=df["High"], low=df["Low"], close=close
    ).average_true_range().iloc[-1]

    return {
        "current_price": round(current_price, 2),
        "ma_50": round(ma_50, 2),
        "ma_200": round(ma_200, 2) if ma_200 else "N/A",
        "price_vs_ma50": "above" if current_price > ma_50 else "below",
        "price_vs_ma200": "above" if ma_200 and current_price > ma_200 else "below" if ma_200 else "N/A",
        "rsi": round(rsi, 2),
        "rsi_signal": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral",
        "macd": round(macd, 4),
        "macd_signal_line": round(macd_signal, 4),
        "macd_crossover": "bullish" if macd > macd_signal else "bearish",
        "bb_upper": round(bb_upper, 2),
        "bb_lower": round(bb_lower, 2),
        "atr": round(atr, 2),
    }


@tool
def get_analyst_recommendation(ticker:str) -> dict:
    """Get analyst buy/sell/hold recommendations for an Indian NSE stock
    showing the latest consensus and recommendation trend."""
    ticker = format_ticker(ticker)
    stock = yf.Ticker(ticker)
    rec = stock.recommendations

    if rec is None or rec.empty:
        return {"error": f"No analyst recommendations for {ticker}"}
    
    latest = rec.iloc[-4:]
    summary = latest.to_dict(orient="records")
    return {"recommendations": summary}