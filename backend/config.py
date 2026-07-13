import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# GROQ_MODEL = "groq:llama-3.3-70b-versatile"
GROQ_MODEL = "google_genai:gemini-3.1-flash-lite"
# GROQ_MODEL = "groq:openai/gpt-oss-20b"

NSE_SUFFIX = ".NS"

TEMPERATURE = 0.3

def format_ticker(ticker:str) -> str:
    """Ensure ticker has .NS suffix for NSE."""
    ticker = ticker.upper().strip()
    if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
        return ticker+NSE_SUFFIX
    return ticker

# Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ai-investment-committee/1.0")

COMMITTEE_AGENTS = [
    "fundamental_analyst",
    "technical_analyst",
    "news_analyst",
    "sentiment_analyst",
    "risk_manager",
    "economist",
]

VOTE_WEIGHTS = {
    "fundamental_analyst": 0.25,
    "technical_analyst": 0.15,
    "news_analyst": 0.15,
    "sentiment_analyst": 0.10,
    "risk_manager": 0.20,
    "economist": 0.15,
}