from typing import TypedDict,Annotated
import operator
from pydantic import BaseModel,Field

class AgentVote(BaseModel):
    """ Schema Structure of the Agent Response."""
    agent: str = Field(description="The Name of The Agent(fundamental_analyst/economist/news_analyst/risk_manager/sentiment_analyst/technical_analyst)")
    vote: str = Field(description="The Vote the agent (BUY/SELL/HOLD) ")
    confidence: float = Field(description="The Confidence of the Agent on the Vote.")
    reasoning: str = Field(description="The Reasoning of the Agent")
    key_findings: list[list] 
    price_target: float | None = Field(None,description="The Target Price of the Stock.")

class TeamState(BaseModel):
    """Schema of the Graph Response. """
    #Input
    ticker: str = Field(description="The Stock Market Symbol of the Company.")
    query: str = Field(description="The query of the user.")

    #Agent Votes Accumulated
    votes: Annotated[list[AgentVote], operator.add]

    # Individual Agent Msgs
    messages: Annotated[list,operator.add]

    # # Final Output
    final_decision: str
    final_reasoning: str
    final_price_target: float | None
    team_summary: str


class FinalOutput(BaseModel):
    """Schema of Final Response to be given by the Portfolio Manager."""

    final_decision: str = Field(description="The Final Decision taken by the Agent.")
    final_reasoning: str = Field(description="The Final Investment Thesis.")
    final_price_target: float | None = Field(None,description="The Final Price Target of the Stock.")
    team_summary: str = Field(description="The brief summary of how each analyst voted and key debate points.")