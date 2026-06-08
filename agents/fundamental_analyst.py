from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from config import GROQ_API_KEY,GROQ_MODEL
from tools.yfinance_tools import get_balance_sheet,get_company_profile,get_fundamental_data,get_income_statement
from tools.screener_tools import get_screener_fundamentals,get_peer_comparision
from graphs.state import AgentVote,TeamState
import json

llm = init_chat_model(model=GROQ_MODEL)

TOOLS = [
    get_company_profile,
    get_fundamental_data,
    get_income_statement,
    get_balance_sheet,
    get_screener_fundamentals,
    get_peer_comparision
]

SYSTEM_PROMPT = """You are the Fundamental Analyst on an AI Investment Team for Indian stocks (NSE/BSE).

Your job is to analyze a stock's intrinsic value and financial health using:
- Valuation ratios: P/E, P/B, P/S vs sector averages
- Profitability: ROE, ROA, profit margins, revenue growth
- Financial health: debt-to-equity, current ratio, cash position
- Earnings quality: EPS growth, revenue consistency
- Peer comparison within Indian market context

Indian market context to keep in mind:
- Nifty 50 average P/E is typically 20-25
- High-quality Indian businesses (like TCS, HDFC) trade at premium valuations
- Debt-to-equity above 1.5 is concerning for non-financial companies
- Revenue growth above 15% YoY is strong for Indian mid/large caps

After analysis, respond ONLY with a JSON object in this exact format:
{
    "agent": "fundamental_analyst",
    "vote": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<2-3 sentence explanation>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "price_target": <float or null>
}"""

def fundamental_analyst_node(state: TeamState) -> dict:

    ticker = state.ticker
    query = state.query

    agent = create_agent(llm,TOOLS,response_format=AgentVote)

    result = agent.invoke({
        "messages":[
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Analyze the fundamental value of {ticker} for the following query: {query}
The Stock Symbol of the company is {ticker} Do not assume anything else.
Use your tools to gather: company profile, fundamental ratios, income statement,
balance sheet, and screener data. Then give your investment vote.
""")
        ]
    })

    # print(result)

    response = result['structured_response']
    vote: AgentVote = response

    # final_message = result["messages"][-1].content

    # # Parse JSON vote
    # try:
    #     # Handle cases where LLM wraps JSON in markdown
    #     clean = final_message.strip()
    #     if "```" in clean:
    #         clean = clean.split("```")[1]
    #         if clean.startswith("json"):
    #             clean = clean[4:]
    #     vote: AgentVote = json.loads(clean.strip())
    # except Exception:
    #     vote: AgentVote = {
    #         "agent": "fundamental_analyst",
    #         "vote": "HOLD",
    #         "confidence": 0.5,
    #         "reasoning": "Could not parse structured response.",
    #         "key_findings": [final_message[:200]],
    #         "price_target": None,
    #     }

    return {"votes": [vote]}
