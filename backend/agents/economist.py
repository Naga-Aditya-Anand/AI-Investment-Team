from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
# from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware
from agents.middleware import ToolCallLimitMiddleware
from config import GROQ_MODEL,TEMPERATURE
from graphs.state import AgentVote,TeamState
import json
from tools.tavily_tools import search_india_marco_news,search_sector_outlook
from tools.yfinance_tools import get_company_profile

llm = init_chat_model(model=GROQ_MODEL,temperature=TEMPERATURE)

TOOLS = [
    search_sector_outlook,
    search_india_marco_news,
    get_company_profile,
]

tool_limit_guard = ToolCallLimitMiddleware(max_tool_calls=3)

SYSTEM_PROMPT = """You are the Economist on an AI Investment Committee for Indian stocks (NSE/BSE).

Your job is to assess macroeconomic and sector-level tailwinds/headwinds:
- RBI monetary policy: repo rate direction (rate cuts = positive for markets)
- India GDP growth trajectory and consumption trends
- Inflation impact on margins and consumer spending
- FII/DII flows into Indian equities
- Sector-specific government policy (PLI schemes, import duties, subsidies)
- Global factors: US Fed policy, crude oil prices, China competition

Macro tailwinds for Indian stocks:
- RBI rate cut cycle → positive for rate-sensitive sectors (banking, real estate, auto)
- Strong GDP growth → positive for consumption, infrastructure
- PLI scheme beneficiaries → manufacturing, electronics, pharma
- Weak rupee → positive for IT exporters, negative for import-heavy companies

CRITICAL TOOL RULES:
1. Call each tool exactly once. Do not call the same tool twice, even if you want to verify data.
2. If you receive a system or middleware error stating that a tool call limit has been reached, you must STOP immediately. Do not try to call that tool or any other tool again.

FINAL RESPONSE PROTOCOL:
After your analysis (or immediately upon hitting a tool limit error), respond ONLY with a JSON object in this exact format. No conversational text before or after the JSON:

After analysis, respond ONLY with a JSON object in this exact format:
{
    "agent": "economist",
    "vote": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<2-3 sentence explanation>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "price_target": null
}"""


def economist_node(state: TeamState) -> dict:
    ticker = state.ticker
    query = state.query

    agent = create_agent(llm, TOOLS,middleware=[tool_limit_guard],response_format=AgentVote)

    # Get sector info first for targeted macro analysis
    profile = get_company_profile.invoke({"ticker": ticker})
    sector = profile.get("sector", "unknown") if isinstance(profile, dict) else "unknown"

    result = agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Analyze the macroeconomic environment for {ticker} (Sector: {sector}) regarding: {query}
The Stock Symbol of the company is {ticker} Do not assume anything else.
Use your tools to get India macro news and sector outlook.
Assess how current macro conditions affect this stock's prospects.
Then give your macro-driven investment vote.
""")
        ]
    })

    print(result)

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
    #         "agent": "economist",
    #         "vote": "HOLD",
    #         "confidence": 0.5,
    #         "reasoning": "Could not parse structured response.",
    #         "key_findings": [final_message[:200]],
    #         "price_target": None,
    #     }


    return {"votes": [vote]}