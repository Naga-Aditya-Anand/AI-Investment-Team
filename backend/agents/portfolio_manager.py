from langchain.chat_models import init_chat_model
from config import GROQ_MODEL,VOTE_WEIGHTS,TEMPERATURE
from langchain.messages import SystemMessage,HumanMessage
from graphs.state import TeamState,FinalOutput
import json

llm = init_chat_model(model=GROQ_MODEL,temperature=TEMPERATURE)
llm_str_out = llm.with_structured_output(FinalOutput)

SYSTEM_PROMPT = """You are the Portfolio Manager and Chairman of an AI Investment Committee for Indian stocks.

You receive votes from 6 specialist analysts and make the final investment decision.
Your job is to:
1. Weigh each analyst's vote by their confidence and domain weight
2. Identify consensus and disagreements
3. Make a final BUY / SELL / HOLD decision
4. Set a price target range if analysts provided targets
5. Write a clear, actionable investment thesis

Be decisive. Acknowledge minority views but commit to a clear recommendation.
Always include a disclaimer that this is AI-generated analysis, not financial advice.

Call each tool exactly once. Do not call the same tool twice, even if you want to verify data.

Respond ONLY with a JSON object in this exact format:
{
    "final_decision": "BUY" or "SELL" or "HOLD",
    "confidence": <float between 0.0 and 1.0>,
    "final_reasoning": "<3-4 sentence investment thesis>",
    "price_target": <float or null>,
    "committee_summary": "<brief summary of how each analyst voted and key debate points>",
    "disclaimer": "This is AI-generated analysis for educational purposes only, not financial advice."
}"""


def calculate_weighted_score(votes: list, weights:dict) -> float:
    """Convert votes to weighted score: BUY=1, HOLD=0, SELL=-1"""

    vote_map = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}
    total_weight = 0
    weighted_sum = 0
    print(votes)
    for vote in votes:
        agent = vote.agent
        weight = weights.get(agent,0.15)
        confidence = vote.confidence
        vote_value = vote_map.get(vote.vote,0.0)
        # agent = vote.get("agent", "")
        # weight = weights.get(agent, 0.15)
        # confidence = vote.get("confidence", 0.5)
        # vote_value = vote_map.get(vote.get("vote", "HOLD"), 0.0)
        weighted_sum += vote_value * weight * confidence
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0 else 0.0

def portfolio_manager_node(state: TeamState) -> dict:
    votes = state.votes
    ticker = state.ticker
    query = state.query

    weighted_score = calculate_weighted_score(votes,VOTE_WEIGHTS)

    price_targets = [
        v.price_target for v in votes
        if v.price_target is not None
    ]

    avg_price_target = (
        round(sum(price_targets) / len(price_targets), 2)
        if price_targets else None
    )

    votes_text = json.dumps([v.model_dump_json(indent=2) for v in votes])

    result = llm_str_out.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Stock: {ticker}
User Query: {query}

Committee Votes:
{votes_text}

Weighted Score (BUY=positive, SELL=negative): {weighted_score:.3f}
Average Analyst Price Target: {avg_price_target}

As Portfolio Manager, synthesize these votes and make the final investment decision.
""")
    ])


    # final_message = result.content

    # try:
    #     clean = final_message.strip()
    #     if "```" in clean:
    #         clean = clean.split("```")[1]
    #         if clean.startswith("json"):
    #             clean = clean[4:]
    #     decision = json.loads(clean.strip())
    # except Exception:
    #     # Fallback based on weighted score
    #     fallback_vote = "BUY" if weighted_score > 0.2 else "SELL" if weighted_score < -0.2 else "HOLD"
    #     decision = {
    #         "final_decision": fallback_vote,
    #         "confidence": 0.5,
    #         "final_reasoning": final_message[:300],
    #         "price_target": avg_price_target,
    #         "committee_summary": f"Weighted score: {weighted_score:.3f}",
    #         "disclaimer": "This is AI-generated analysis for educational purposes only, not financial advice.",
    #     }

    # return {
    #     "final_decision": decision.get("final_decision", "HOLD"),
    #     "final_reasoning": decision.get("final_reasoning", ""),
    #     "final_price_target": decision.get("price_target", avg_price_target),
    #     "committee_summary": decision.get("committee_summary", ""),
    # }
    
    return {
        "final_decision": result.final_decision,
        "final_reasoning": result.final_reasoning,
        "final_price_target": result.final_price_target,
        "team_summary": result.team_summary
    }