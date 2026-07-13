from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
# from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware
from agents.middleware import ToolCallLimitMiddleware
from config import GROQ_MODEL,TEMPERATURE
from graphs.state import AgentVote,TeamState
import json
from tools.yfinance_tools import get_technical_indicators,get_analyst_recommendation,get_current_price

llm = init_chat_model(model=GROQ_MODEL,temperature=TEMPERATURE)

TOOLS = [
    get_current_price,
    get_analyst_recommendation,
    get_technical_indicators,
]

tool_limit_guard = ToolCallLimitMiddleware(max_tool_calls=3)

SYSTEM_PROMPT = """You are the Technical Analyst on an AI Investment Team for Indian stocks (NSE/BSE).

Your job is to analyze price action and momentum using:
- Trend: Price vs MA50, MA200 (golden cross / death cross)
- Momentum: RSI (overbought >70, oversold <30), MACD crossovers
- Volatility: Bollinger Bands position, ATR
- Support/Resistance: 52-week high/low levels

Technical signals to weigh:
- RSI 30-70 with bullish MACD crossover → strong BUY signal
- Price above both MA50 and MA200 → bullish trend
- Price near 52-week high with high volume → breakout potential
- RSI >80 with bearish MACD → overbought, consider SELL/HOLD

CRITICAL TOOL RULES:
1. Call each tool exactly once. Do not call the same tool twice, even if you want to verify data.
2. If you receive a system or middleware error stating that a tool call limit has been reached, you must STOP immediately. Do not try to call that tool or any other tool again.

FINAL RESPONSE PROTOCOL:
After your analysis (or immediately upon hitting a tool limit error), respond ONLY with a JSON object in this exact format. No conversational text before or after the JSON:

After analysis, respond ONLY with a JSON object in this exact format:
{
    "agent": "technical_analyst",
    "vote": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<2-3 sentence explanation>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "price_target": <float or null>
}"""


def technical_analyst_node(state: TeamState) -> dict:
    ticker = state.ticker
    query = state.query

    agent = create_agent(llm,TOOLS,middleware=[tool_limit_guard],response_format=AgentVote)

    result = agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
Analyze the technical setup of {ticker} for the following query: {query}
The Stock Symbol of the company is {ticker} Do not assume anything else.
Use your tools to gather technical indicators, current price data,
and analyst recommendations. Then give your investment vote.
""")
        ]
    })

    response = result['structured_response']
    vote: AgentVote = response

    # final_msg = result["messages"][-1].content

    # try:
    #     clean = final_msg.strip()
    #     if "```" in clean:
    #         clean = clean.split("```")[1]
    #         if clean.startswith("json"):
    #             clean = clean[4:]
    #     vote: AgentVote = json.loads(clean.strip())
    # except Exception:
    #     vote: AgentVote = {
    #         "agent": "technical_analyst",
    #         "vote": "HOLD",
    #         "confidence": 0.5,
    #         "reasoning": "Could not parse structured response.",
    #         "key_findings": [final_msg[:200]],
    #         "price_target": None,
    #     }

    return {"votes": [vote]}
