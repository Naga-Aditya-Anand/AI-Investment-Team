from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
# from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware
from agents.middleware import ToolCallLimitMiddleware
from config import GROQ_MODEL,TEMPERATURE
from graphs.state import AgentVote,TeamState
import json
from tools.yfinance_tools import get_company_profile,get_fundamental_data,get_balance_sheet,get_technical_indicators
from tools.tavily_tools import search_stock_news

llm = init_chat_model(model=GROQ_MODEL,temperature=TEMPERATURE)

TOOLS = [
    get_technical_indicators,
    get_balance_sheet,
    get_company_profile,
    get_fundamental_data,
    search_stock_news,
]

tool_limit_guard = ToolCallLimitMiddleware(max_tool_calls=5)

SYSTEM_PROMPT = """You are the Risk Manager on an AI Investment Committee for Indian stocks (NSE/BSE).

Your job is to identify and quantify risks before any investment:
- Market risk: Beta, volatility (ATR), drawdown from 52-week high
- Financial risk: Debt-to-equity, interest coverage, cash burn
- Business risk: Sector cyclicality, competition, regulatory exposure
- Governance risk: Promoter pledging, related party transactions, SEBI history
- Liquidity risk: Trading volume, market cap (small cap vs large cap risk)

Indian market specific risks:
- High promoter pledging (>30%) is a red flag
- NBFC/real estate stocks carry higher financial risk
- PSU stocks have policy/political risk
- Small/mid caps have higher liquidity risk
- Rupee depreciation impacts import-heavy companies

Your vote reflects risk-adjusted attractiveness:
- BUY = low risk, good risk/reward
- HOLD = moderate risk, balanced
- SELL = high risk, unfavorable risk/reward

CRITICAL TOOL RULES:
1. Call each tool exactly once. Do not call the same tool twice, even if you want to verify data.
2. If you receive a system or middleware error stating that a tool call limit has been reached, you must STOP immediately. Do not try to call that tool or any other tool again.

FINAL RESPONSE PROTOCOL:
After your analysis (or immediately upon hitting a tool limit error), respond ONLY with a JSON object in this exact format. No conversational text before or after the JSON:

After analysis, respond ONLY with a JSON object in this exact format:
{
    "agent": "risk_manager",
    "vote": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<2-3 sentence explanation>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "price_target": null
}"""


def risk_manager_node(state: TeamState) -> dict:

    ticker = state.ticker
    query = state.query

    agent = create_agent(llm, TOOLS,middleware=[tool_limit_guard],response_format=AgentVote)

    result = agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Perform a comprehensive risk assessment for {ticker} regarding: {query}
The Stock Symbol of the company is {ticker} Do not assume anything else.
Use your tools to assess: beta/volatility, financial leverage,
balance sheet health, recent risk-related news. Then give your risk-adjusted vote.
""")
        ]
    })

    response = result['structured_response']
    vote: AgentVote = response

    # final_message = result["messages"][-1].content

    # try:
    #     clean = final_message.strip()
    #     if "```" in clean:
    #         clean = clean.split("```")[1]
    #         if clean.startswith("json"):
    #             clean = clean[4:]
    #     vote: AgentVote = json.loads(clean.strip())
    # except Exception:
    #     vote: AgentVote = {
    #         "agent": "risk_manager",
    #         "vote": "HOLD",
    #         "confidence": 0.5,
    #         "reasoning": "Could not parse structured response.",
    #         "key_findings": [final_message[:200]],
    #         "price_target": None,
    #     }

    return {"votes": [vote]}