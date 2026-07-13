from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
# from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware
from agents.middleware import ToolCallLimitMiddleware
from config import GROQ_MODEL,TEMPERATURE
from graphs.state import AgentVote,TeamState
import json
from tools.tavily_tools import search_stock_news,search_analyst_ratings,search_bse_filings

llm = init_chat_model(model=GROQ_MODEL,temperature=TEMPERATURE)

TOOLS = [
    search_bse_filings,
    search_analyst_ratings,
    search_stock_news,
]

tool_limit_guard = ToolCallLimitMiddleware(max_tool_calls=3)

SYSTEM_PROMPT = """You are the News Analyst on an AI Investment Committee for Indian stocks (NSE/BSE).

Your job is to analyze recent news flow and corporate events:
- Earnings results: beats/misses vs estimates
- Management guidance: raised/lowered outlook
- Corporate actions: buybacks, dividends, splits, mergers, acquisitions
- Regulatory: SEBI actions, promoter pledging, insider trading disclosures
- Analyst upgrades/downgrades from Indian brokerages

Positive signals: earnings beat, buyback announcement, management guidance upgrade,
analyst upgrades, new contracts/orders, debt reduction.

Negative signals: earnings miss, promoter stake sale, high pledging, SEBI notices,
management exits, guidance cuts, rising competition.

CRITICAL TOOL RULES:
1. Call each tool exactly once. Do not call the same tool twice, even if you want to verify data.
2. If you receive a system or middleware error stating that a tool call limit has been reached, you must STOP immediately. Do not try to call that tool or any other tool again.

FINAL RESPONSE PROTOCOL:
After your analysis (or immediately upon hitting a tool limit error), respond ONLY with a JSON object in this exact format. No conversational text before or after the JSON:

After analysis, respond ONLY with a JSON object in this exact format:
{
    "agent": "news_analyst",
    "vote": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<2-3 sentence explanation>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "price_target": <float or null>
}"""


def news_analyst_node(state: TeamState) -> dict:

    ticker = state.ticker
    query = state.query

    agent = create_agent(llm,TOOLS,middleware=[tool_limit_guard],response_format=AgentVote)

    result = agent.invoke({
        "messages":[
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Analyze the recent news and corporate events for {ticker} regarding: {query}
The Stock Symbol of the company is {ticker} Do not assume anything else.
Use your tools to search for latest news, analyst ratings,
and BSE/NSE filings. Then give your investment vote.
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
    #         "agent": "news_analyst",
    #         "vote": "HOLD",
    #         "confidence": 0.5,
    #         "reasoning": "Could not parse structured response.",
    #         "key_findings": [final_message[:200]],
    #         "price_target": None,
    #     }

    return {"votes": [vote]}