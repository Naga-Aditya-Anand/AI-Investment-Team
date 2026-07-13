from graphs.team_graph import team_graph
import json
import asyncio
import uuid


async def run_committee(ticker: str, query: str) -> dict:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    initial_state = {
        "ticker": ticker.upper(),
        "query": query,
        "votes": [],
        "messages": [],
        "final_decision": "",
        "final_reasoning": "",
        "final_price_target": None,
        "team_summary": "",
    }

    print(f"\n🏛️  AI Investment Committee convened for {ticker.upper()}")
    print(f"📋 Query: {query}")
    print("=" * 60)
    print("⏳ Analysts researching... (this takes ~30-60 seconds)\n")



    async for event in team_graph.astream_events(input=initial_state,config=config):
        print(event)
            

    # result = team_graph.invoke(initial_state, config=config)

    # # Print individual votes
    # print("\n📊 COMMITTEE VOTES:")
    # print("-" * 60)
    # for vote in result["votes"]:
    #     emoji = "🟢" if vote.vote == "BUY" else "🔴" if vote.vote == "SELL" else "🟡"
    #     print(f"{emoji} {vote.agent.upper().replace('_', ' ')}: {vote.vote} "
    #           f"(confidence: {vote.confidence:.0%})")
    #     print(f"   → {vote.reasoning}")
    #     if vote.price_target:
    #         print(f"   💰 Price Target: ₹{vote.price_target}")
    #     print()

    # # Print final decision
    # print("=" * 60)
    # print("🏛️  PORTFOLIO MANAGER FINAL DECISION:")
    # print("-" * 60)
    # decision = result["final_decision"]
    # emoji = "🟢" if decision == "BUY" else "🔴" if decision == "SELL" else "🟡"
    # print(f"{emoji} DECISION: {decision}")
    # if result.get("final_price_target"):
    #     print(f"💰 Price Target: ₹{result['final_price_target']}")
    # print(f"\n📝 Thesis: {result['final_reasoning']}")
    # print(f"\n🗳️  Team Summary: {result['team_summary']}")
    # print("\n⚠️  Disclaimer: AI-generated analysis. Not financial advice.")

    # return result


if __name__ == "__main__":
    # Test run
    # result = run_committee(
    #     ticker="SYRMA.NS",
    #     query="Should I buy SYRMA stock right now?"
    # )

    asyncio.run(
        run_committee(
            ticker="ETERNAL.NS",
            query="Should I buy?"
        )
    )