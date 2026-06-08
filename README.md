# 🏛️ AI Investment Team
### Multi-Agent Financial Analysis System for Indian Equities (NSE)

A production-grade multi-agent system that convenes a committee of six specialized AI analysts to evaluate any NSE-listed stock. Each analyst independently researches the stock from their domain, casts a weighted vote, and the Portfolio Manager synthesizes a final consensus decision — **BUY / SELL / HOLD** — complete with a price target and investment thesis.

---

## 📐 Architecture

The committee runs a **parallel fan-out → fan-in** workflow orchestrated by LangGraph:

```
                  ┌──────────────── START ─────────────────┐
                  │                                        │
                  ├──► Fundamental Analyst ────────────────┤
                  ├──► Technical Analyst ───────────────────┤
                  ├──► News Analyst ────────────────────────┤──► Portfolio Manager ──► END
                  ├──► Sentiment Analyst ──────────────────┤
                  ├──► Risk Manager ────────────────────────┤
                  └──► Economist ──────────────────────────┘
```

All six analysts run **concurrently** using LangGraph's `Send` API. Each agent uses its own LLM instance, a tailored set of tools, and a domain-specific system prompt. Votes accumulate in shared state via `Annotated[list, operator.add]` and are passed to the Portfolio Manager for final synthesis.

---

## 🗳️ Committee Agents & Weights

| Agent | Weight | Responsibility |
|:---|:---:|:---|
| **Fundamental Analyst** | 25% | P/E, ROE, EPS, revenue growth, DCF, peer comparison |
| **Risk Manager** | 20% | Beta, ATR volatility, debt ratios, promoter pledging, liquidity risk |
| **Technical Analyst** | 15% | MA 50/200, RSI, MACD crossover, Bollinger Bands |
| **News Analyst** | 15% | Earnings results, SEBI/BSE filings, analyst upgrades/downgrades |
| **Economist** | 15% | RBI repo rate, India GDP, inflation, sector-level policy tailwinds |
| **Sentiment Analyst** | 10% | Reddit buzz on r/IndiaInvestments, r/DalalStreet, r/IndianStockMarket |

Weights reflect institutional practice — fundamental and risk analysis carry more conviction than sentiment signals.

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| Agent Orchestration | LangGraph (StateGraph + Send API) |
| LLM Inference | Gemini — `gemini-3.1-flash-lite` |
| Agent Framework | LangChain (`create_react_agent`, `bind_tools`) |
| Financial Data | yfinance (price, OHLCV, financials) |
| Technical Indicators | `ta` (RSI, MACD, Bollinger Bands, ATR) |
| News & Web Search | Tavily (earnings, analyst ratings, BSE filings) |
| Fundamentals | Screener.in via Tavily search |
| Sentiment | PRAW — Reddit API |
| UI | Streamlit |
| Package Manager | uv |

---

## 📂 Project Structure

```
ai-investment-committee/
├── agents/
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   ├── news_analyst.py
│   ├── sentiment_analyst.py
│   ├── risk_manager.py
│   ├── economist.py
│   └── portfolio_manager.py
├── graphs/
│   ├── state.py               # Pydantic schemas (AgentVote, FinalOutput, TeamState)
│   └── team_graph.py          # LangGraph DAG — fan-out, fan-in, compilation
├── tools/
│   ├── yfinance_tools.py      # Price, technicals, fundamentals
│   ├── screener_tools.py      # Screener.in fundamentals via Tavily
│   ├── tavily_tools.py        # News, analyst ratings, BSE filings, macro
│   └── reddit_tools.py        # Reddit sentiment across Indian subreddits
├── ui/
│   └── app.py                 # Streamlit dashboard
├── config.py                  # Models, weights, ticker formatting
├── main.py                    # CLI entrypoint
├── .env.example
└── pyproject.toml
```

---

## ⚙️ Setup

### Prerequisites
- Python `>= 3.13`
- [`uv`](https://github.com/astral-sh/uv) package manager

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

```bash
git clone https://github.com/yourusername/ai-investment-committee
cd ai-investment-committee
uv venv && uv sync
```

### API Keys

Copy `.env.example` to `.env` and fill in:

```env
GROQ_API_KEY=          # console.groq.com
TAVILY_API_KEY=        # tavily.com
```

---

## 🚀 Running

### Streamlit UI (Recommended)

```bash
uv run streamlit run ui/app.py
```

Opens at `http://localhost:8501`. Enter any NSE ticker and your question — the committee convenes, all six analysts research in parallel, and results render with individual vote cards, confidence bars, a vote tally, and the final decision.

### CLI

```bash
uv run python main.py
```

Runs a sample analysis and prints all agent votes + final decision to terminal.

---

## 📊 Output Format

Each analyst returns a structured vote:

```json
{
  "agent": "fundamental_analyst",
  "vote": "BUY",
  "confidence": 0.82,
  "reasoning": "Strong revenue growth, P/E below sector average, healthy balance sheet.",
  "key_findings": [
    "P/E of 18.4x vs sector average of 24x",
    "Revenue grew 21% YoY, net margins expanding",
    "Debt-to-equity at 0.3 — conservative leverage"
  ],
  "price_target": 1450.00
}
```

The Portfolio Manager synthesizes all votes using weighted scoring and outputs:

```json
{
  "final_decision": "BUY",
  "final_reasoning": "4 of 6 analysts voted BUY with high conviction...",
  "final_price_target": 1480.00,
  "team_summary": "Fundamental and Risk both strongly bullish. Economist neutral on macro..."
}
```

---

## ⚠️ Limitations

- yfinance data can be inconsistent or delayed for some NSE tickers
- Reddit sentiment signal is low-volume for Indian mid/small caps
- Price targets are LLM estimates based on analyst reasoning, not quantitative models
- Macro data relies on Tavily web search — not a live RBI data feed

---

## 📄 Disclaimer

This project is built for **educational purposes** and portfolio demonstration only. It does not constitute financial advice. Always consult a SEBI-registered financial advisor before making investment decisions.