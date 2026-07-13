import praw
from langchain_core.tools import tool
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,format_ticker

reddit = praw.Reddit(
    client_id = REDDIT_CLIENT_ID,
    client_secret = REDDIT_CLIENT_SECRET,
    user_agent = REDDIT_USER_AGENT,
)

INDIA_SUBREDDITS = [
    "IndiaInvestments",
    "DalalStreet",
    "IndianStockMarket",
    "stocks",
]


@tool
def get_reddit_sentiment(ticker: str) -> dict:
    """Search Indian investment subreddits for retail investor sentiment,
    discussions and opinions about an Indian stock on Reddit."""

    ticker_clean = format_ticker(ticker).upper().replace(".NS", "").replace(".BO", "")
    posts = []
    bullish, bearish, neutral = 0, 0, 0

    bull_words = ["buy", "bull", "long", "calls", "upside", "growth",
                  "strong", "accumulate", "target", "breakout"]
    bear_words = ["sell", "bear", "short", "puts", "crash", "overvalued",
                  "dump", "avoid", "exit", "weak", "fall"]
    
    for subreddit_name in INDIA_SUBREDDITS:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.search(
                ticker_clean, limit=5, sort="hot", time_filter="month"
            ):
                title_lower = post.title.lower()
                score = (
                    sum(1 for w in bull_words if w in title_lower) - sum(1 for w in bear_words if w in title_lower)
                )

                sentiment = "bullish" if score > 0 else "bearish" if score < 0 else "neutral"
                if sentiment == "bullish": bullish += 1
                elif sentiment == "bearish": bearish += 1
                else: neutral += 1

                posts.append(
                    {"subreddit": subreddit_name,
                    "title": post.title,
                    "upvotes": post.score,
                    "comments": post.num_comments,
                    "sentiment": sentiment,}
                )
        except Exception:
            continue

    total = len(posts) or 1

    return {
        "total_posts_analyzed": total,
        "bullish_pct": round(bullish / total * 100, 1),
        "bearish_pct": round(bearish / total * 100, 1),
        "neutral_pct": round(neutral / total * 100, 1),
        "overall_sentiment": (
            "bullish" if bullish > bearish
            else "bearish" if bearish > bullish
            else "neutral"
        ),
        "top_posts": sorted(posts, key=lambda x: x["upvotes"], reverse=True)[:5],
    }
