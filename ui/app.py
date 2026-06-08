import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.team_graph import team_graph
import uuid
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Investment Team",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6e0;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }

/* Hero title */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    line-height: 1.1;
    color: #f0ede6;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #c9a84c;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

/* Input area */
.input-card {
    background: #13131a;
    border: 1px solid #2a2a35;
    border-radius: 12px;
    padding: 1.8rem;
    margin-bottom: 2rem;
}

/* Divider */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #c9a84c55, transparent);
    margin: 2rem 0;
}

/* Vote card */
.vote-card {
    background: #13131a;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    border-left: 4px solid transparent;
    transition: transform 0.2s;
}
.vote-card:hover { transform: translateX(4px); }
.vote-card.buy  { border-left-color: #22c55e; }
.vote-card.sell { border-left-color: #ef4444; }
.vote-card.hold { border-left-color: #f59e0b; }

.vote-agent {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.3rem;
}
.vote-verdict {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    margin-bottom: 0.4rem;
}
.vote-verdict.buy  { color: #22c55e; }
.vote-verdict.sell { color: #ef4444; }
.vote-verdict.hold { color: #f59e0b; }
.vote-reasoning {
    font-size: 0.85rem;
    color: #aaa;
    line-height: 1.5;
    margin-bottom: 0.6rem;
}
.vote-findings {
    font-size: 0.78rem;
    color: #777;
    font-family: 'DM Mono', monospace;
}
.vote-target {
    display: inline-block;
    margin-top: 0.5rem;
    background: #1e1e2a;
    border: 1px solid #2a2a35;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #c9a84c;
}

/* Confidence bar */
.conf-bar-bg {
    background: #1e1e2a;
    border-radius: 99px;
    height: 4px;
    margin-top: 0.5rem;
}
.conf-bar-fill {
    height: 4px;
    border-radius: 99px;
    background: linear-gradient(90deg, #c9a84c, #f0c96a);
}

/* Final decision card */
.final-card {
    background: #13131a;
    border: 1px solid #2a2a35;
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.final-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #c9a84c, #f0c96a, #c9a84c);
}
.final-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #c9a84c;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.final-verdict {
    font-family: 'DM Serif Display', serif;
    font-size: 4rem;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.final-verdict.BUY  { color: #22c55e; }
.final-verdict.SELL { color: #ef4444; }
.final-verdict.HOLD { color: #f59e0b; }
.final-thesis {
    font-size: 0.92rem;
    color: #aaa;
    max-width: 600px;
    margin: 1rem auto 0;
    line-height: 1.7;
}
.final-target {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: #c9a84c;
    margin-top: 1rem;
}

/* Tally bar */
.tally-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
}
.tally-label { width: 40px; color: #888; }
.tally-bg {
    flex: 1;
    background: #1e1e2a;
    border-radius: 99px;
    height: 8px;
}
.tally-fill { height: 8px; border-radius: 99px; }
.tally-count { width: 20px; text-align: right; color: #aaa; }

/* Disclaimer */
.disclaimer {
    font-size: 0.72rem;
    color: #555;
    font-family: 'DM Mono', monospace;
    margin-top: 1.5rem;
    text-align: center;
}

/* Agent status during loading */
.agent-status {
    background: #13131a;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 0.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #666;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

/* Streamlit overrides */
.stTextInput > div > div > input {
    background: #1a1a24 !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 8px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea > div > div > textarea {
    background: #1a1a24 !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 8px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #f0c96a) !important;
    color: #0a0a0f !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

AGENT_LABELS = {
    "fundamental_analyst": "Fundamental Analyst",
    "technical_analyst":   "Technical Analyst",
    "news_analyst":        "News Analyst",
    "sentiment_analyst":   "Sentiment Analyst",
    "risk_manager":        "Risk Manager",
    "economist":           "Economist",
}

AGENT_ICONS = {
    "fundamental_analyst": "📊",
    "technical_analyst":   "📈",
    "news_analyst":        "📰",
    "sentiment_analyst":   "💬",
    "risk_manager":        "🛡️",
    "economist":           "🌐",
}


def render_vote_card(vote: dict):
    verdict = vote.vote.upper()
    css_class = verdict.lower()
    agent_key = vote.agent
    label = AGENT_LABELS.get(agent_key, agent_key.replace("_", " ").title())
    icon = AGENT_ICONS.get(agent_key, "🤖")
    confidence = vote.confidence
    reasoning = vote.reasoning
    findings = vote.key_findings
    target = vote.price_target

    findings_html = "".join(f"<div>· {f}</div>" for f in findings[:3])

    target_html = f'<div class="vote-target">&#8377;{target:,.2f} target</div>' if target else ""
    conf_pct = int(confidence * 100)

    html = (
        f'<div class="vote-card {css_class}">'
        f'<div class="vote-agent">{icon} {label}</div>'
        f'<div class="vote-verdict {css_class}">{verdict}</div>'
        f'<div class="vote-reasoning">{reasoning}</div>'
        f'<div class="vote-findings">{findings_html}</div>'
        f'{target_html}'
        f'<div class="conf-bar-bg">'
        f'<div class="conf-bar-fill" style="width:{conf_pct}%"></div>'
        f'</div>'
        f'<div style="font-family:\'DM Mono\',monospace;font-size:0.68rem;color:#555;margin-top:0.3rem">'
        f'{conf_pct}% confidence'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_tally(votes: list):
    counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for v in votes:
        counts[v.vote.upper()] = counts.get(v.vote.upper(), 0) + 1

    total = len(votes) or 1
    colors = {"BUY": "#22c55e", "SELL": "#ef4444", "HOLD": "#f59e0b"}

    for label, color in colors.items():
        count = counts[label]
        pct = int(count / total * 100)
        st.markdown(f"""
        <div class="tally-row">
            <div class="tally-label">{label}</div>
            <div class="tally-bg">
                <div class="tally-fill" style="width:{pct}%;background:{color}"></div>
            </div>
            <div class="tally-count">{count}</div>
        </div>
        """, unsafe_allow_html=True)


def render_final_decision(result: dict):
    decision = result.get("final_decision", "HOLD").upper()
    reasoning = result.get("final_reasoning", "")
    target = result.get("final_price_target")
    summary = result.get("team_summary", "")

    target_html = f'<div class="final-target">Price Target: ₹{target:,.2f}</div>' if target else ""

    st.markdown(f"""
    <div class="final-card">
        <div class="final-label">Committee Decision</div>
        <div class="final-verdict {decision}">{decision}</div>
        {target_html}
        <div class="final-thesis">{reasoning}</div>
    </div>
    """, unsafe_allow_html=True)

    if summary:
        st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.82rem;color:#777;line-height:1.7;
                    font-family:'DM Sans',sans-serif;padding:0 0.5rem">
            <span style="font-family:'DM Mono',monospace;font-size:0.7rem;
                         color:#c9a84c;letter-spacing:0.1em">COMMITTEE NOTES</span><br><br>
            {summary}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="disclaimer">⚠ AI-generated analysis for educational purposes only. '
        'Not financial advice. Always consult a SEBI-registered advisor.</div>',
        unsafe_allow_html=True
    )


# ── Main UI ───────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">AI Investment<br>Committee</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">NSE · Indian Equities · Multi-Agent Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([1, 2])
with col1:
    ticker = st.text_input(
        "NSE Ticker",
        placeholder="e.g. RELIANCE, TCS, HDFCBANK",
        label_visibility="visible",
    )
with col2:
    query = st.text_area(
        "Your Question",
        placeholder="e.g. Should I buy Reliance right now? What is the price target for TCS?",
        height=100,
        label_visibility="visible",
    )

# Example queries
st.markdown("""
<div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#555;margin-bottom:1rem">
    EXAMPLES →
    &nbsp;&nbsp;Should I buy {ticker} at current price?
    &nbsp;&nbsp;·&nbsp;&nbsp;What is the 12-month price target?
    &nbsp;&nbsp;·&nbsp;&nbsp;Is {ticker} overvalued?
</div>
""", unsafe_allow_html=True)

run_btn = st.button("Convene Committee →")

# ── Execution ─────────────────────────────────────────────────────────────────

if run_btn:
    if not ticker.strip():
        st.error("Please enter a ticker symbol.")
    elif not query.strip():
        st.error("Please enter your question.")
    else:
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # Loading state
        with st.status("🏛️ Committee in session...", expanded=True) as status:
            st.write("📊 Fundamental Analyst gathering financials...")
            st.write("📈 Technical Analyst reading price action...")
            st.write("📰 News Analyst scanning headlines...")
            st.write("💬 Sentiment Analyst polling Reddit...")
            st.write("🛡️ Risk Manager assessing downside...")
            st.write("🌐 Economist reading macro environment...")

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            initial_state = {
                "ticker": ticker.strip().upper(),
                "query": query.strip(),
                "votes": [],
                "messages": [],
                "final_decision": "",
                "final_reasoning": "",
                "final_price_target": None,
                "team_summary": "",
            }

            result = team_graph.invoke(initial_state, config=config)
            status.update(label="✅ Analysis complete", state="complete")

        votes = result.get("votes", [])

        # Layout: votes left, decision right
        left, right = st.columns([1.1, 1], gap="large")

        with left:
            st.markdown("""
            <div style="font-family:'DM Mono',monospace;font-size:0.7rem;
                        color:#c9a84c;letter-spacing:0.15em;margin-bottom:1rem">
                ANALYST VOTES
            </div>
            """, unsafe_allow_html=True)

            # Sort: BUY first, then HOLD, then SELL
            order = {"BUY": 0, "HOLD": 1, "SELL": 2}
            sorted_votes = sorted(votes, key=lambda v: order.get(v.vote, 1))
            for vote in sorted_votes:
                render_vote_card(vote)

        with right:
            st.markdown("""
            <div style="font-family:'DM Mono',monospace;font-size:0.7rem;
                        color:#c9a84c;letter-spacing:0.15em;margin-bottom:1rem">
                FINAL VERDICT
            </div>
            """, unsafe_allow_html=True)
            render_final_decision(result)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'DM Mono',monospace;font-size:0.7rem;
                        color:#c9a84c;letter-spacing:0.15em;margin-bottom:0.8rem">
                VOTE TALLY
            </div>
            """, unsafe_allow_html=True)
            render_tally(votes)