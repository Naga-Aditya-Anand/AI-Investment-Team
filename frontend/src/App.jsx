import { useState, useMemo, useRef } from "react";
import { parse } from "partial-json";

// ──────────────────────────────────────────────────────────────────────────
// Config
// ──────────────────────────────────────────────────────────────────────────

// const API_URL = "http://localhost:8000/stream";
// const PRICE_API_URL = "http://localhost:8000/price"; // separate, fast endpoint — not tied to any analyst node

const API_URL = "https://ai-investment-team-353728531541.asia-south1.run.app/stream";
const PRICE_API_URL = "https://ai-investment-team-353728531541.asia-south1.run.app/price"; // separate, fast endpoint — not tied to any analyst node



// ──────────────────────────────────────────────────────────────────────────
// Meta Data & Colors (Mapped to backend _node keys)
// ──────────────────────────────────────────────────────────────────────────

const AGENT_META = {
  fundamental_analyst_node: { label: "Fundamental", weight: 25 },
  risk_manager_node: { label: "Risk", weight: 20 },
  technical_analyst_node: { label: "Technical", weight: 15 },
  news_analyst_node: { label: "News", weight: 15 },
  economist_node: { label: "Economist", weight: 15 },
  sentiment_analyst_node: { label: "Sentiment", weight: 10 },
};

const VOTE_COLOR = {
  BUY: { ink: "#2f6b4f", soft: "#e7efe8", line: "#2f6b4f" },
  SELL: { ink: "#8c3b3b", soft: "#f3e8e6", line: "#8c3b3b" },
  HOLD: { ink: "#a8842f", soft: "#f3ece0", line: "#a8842f" },
};

function voteColor(vote) {
  return VOTE_COLOR[vote] || VOTE_COLOR.HOLD;
}

// ──────────────────────────────────────────────────────────────────────────
// Visual primitives
// ──────────────────────────────────────────────────────────────────────────

function ConfidenceMeter({ vote, confidence = 0 }) {
  const safeVote = vote || "HOLD";
  const direction = safeVote === "BUY" ? 1 : safeVote === "SELL" ? -1 : 0;
  const position = 50 + direction * confidence * 48;
  const colors = voteColor(safeVote);

  return (
    <div style={{ position: "relative", height: 6, margin: "14px 0 6px" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: 3,
          background: "linear-gradient(to right, #8c3b3b22, #c2c2c200 48%, #c2c2c200 52%, #2f6b4f22)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: -3,
          width: 1,
          height: 12,
          background: "#c9933e55",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: `${position}%`,
          top: -4,
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: colors.ink,
          transform: "translateX(-50%)",
          boxShadow: `0 0 0 3px ${colors.soft}`,
          transition: "left 150ms ease-out",
        }}
      />
    </div>
  );
}

function AgentSeat({ nodeKey, vote, status }) {
  const meta = AGENT_META[nodeKey];
  const colors = voteColor(vote.vote);

  return (
    <div
      style={{
        background: "#f9f6ee",
        border: "1px solid #e3dcc8",
        borderRadius: 4,
        padding: "18px 20px",
        position: "relative",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: 10,
        }}
      >
        <div
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 11,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: "#7a7363",
          }}
        >
          {meta.label} · {meta.weight}%
        </div>
        <div
          style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 22,
            fontWeight: 600,
            color: colors.ink,
          }}
        >
          {vote.vote || "..."}
        </div>
      </div>

      <p
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 13.5,
          lineHeight: 1.6,
          color: "#3a362c",
          margin: "0 0 12px",
          minHeight: 44,
        }}
      >
        {vote.reasoning || <span style={{ opacity: 0.4 }}>Formulating thesis...</span>}
      </p>

      <ul style={{ margin: "0 0 4px", padding: 0, listStyle: "none", minHeight: 60 }}>
        {(vote.key_findings || []).slice(0, 3).map((f, i) => (
          <li
            key={i}
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 11.5,
              color: "#8a8270",
              marginBottom: 3,
              paddingLeft: 12,
              position: "relative",
            }}
          >
            <span style={{ position: "absolute", left: 0 }}>–</span>
            {f}
          </li>
        ))}
      </ul>

      <ConfidenceMeter vote={vote.vote} confidence={vote.confidence || 0} />

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10.5,
          color: "#a39c89",
        }}
      >
        <span>{Math.round((vote.confidence || 0) * 100)}% confidence</span>
        {vote.price_target ? (
          <span style={{ color: "#c9933e" }}>
            target ₹{vote.price_target.toLocaleString("en-IN")}
          </span>
        ) : status === "running" ? (
          <span>calculating target...</span>
        ) : (
          <span>No Target</span>
        )}
      </div>
    </div>
  );
}

function ConsensusLine({ votesArray, final }) {
  return (
    <div style={{ position: "relative", height: 64, margin: "8px 0 0" }}>
      <div
        style={{
          position: "absolute",
          top: 30,
          left: 0,
          right: 0,
          height: 1,
          background: "#d8d0ba",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 24,
          left: "50%",
          width: 1,
          height: 14,
          background: "#c9933e",
        }}
      />

      {votesArray.map((v, i) => {
        const safeVote = v.vote || "HOLD";
        const direction = safeVote === "BUY" ? 1 : safeVote === "SELL" ? -1 : 0;
        const pos = 50 + direction * (v.confidence || 0) * 46;
        return (
          <div
            key={i}
            title={safeVote}
            style={{
              position: "absolute",
              left: `${pos}%`,
              top: 26,
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: voteColor(safeVote).ink,
              transform: "translateX(-50%)",
              opacity: 0.85,
              transition: "left 150ms ease-out",
            }}
          />
        );
      })}

      {final && final.final_decision && (
        (() => {
          const direction = final.final_decision === "BUY" ? 1 : final.final_decision === "SELL" ? -1 : 0;
          const pos = 50 + direction * 0.9 * 46;
          return (
            <div
              style={{
                position: "absolute",
                left: `${pos}%`,
                top: 12,
                transform: "translateX(-50%)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                transition: "left 200ms ease-out",
              }}
            >
              <div
                style={{
                  width: 13,
                  height: 13,
                  borderRadius: "50%",
                  background: voteColor(final.final_decision).ink,
                  border: "2px solid #f9f6ee",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.25)",
                }}
              />
            </div>
          );
        })()
      )}

      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          letterSpacing: "0.08em",
          color: "#a39c89",
        }}
      >
        SELL
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          right: 0,
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          letterSpacing: "0.08em",
          color: "#a39c89",
        }}
      >
        BUY
      </div>
    </div>
  );
}

function Tally({ votesArray }) {
  const counts = useMemo(() => {
    const c = { BUY: 0, SELL: 0, HOLD: 0 };
    votesArray.forEach((v) => {
      const voteVal = v.vote || "HOLD";
      c[voteVal] = (c[voteVal] ?? 0) + 1;
    });
    return c;
  }, [votesArray]);
  const total = votesArray.length || 1;

  return (
    <div>
      {["BUY", "HOLD", "SELL"].map((label) => {
        const count = counts[label];
        const pct = (count / total) * 100;
        return (
          <div
            key={label}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 8,
            }}
          >
            <span
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 11,
                width: 36,
                color: "#7a7363",
              }}
            >
              {label}
            </span>
            <div style={{ flex: 1, height: 5, background: "#e3dcc8", borderRadius: 0 }}>
              <div
                style={{
                  height: 5,
                  width: `${pct}%`,
                  background: VOTE_COLOR[label].ink,
                  transition: "width 200ms ease-out",
                }}
              />
            </div>
            <span
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 11,
                color: "#3a362c",
                width: 12,
                textAlign: "right",
              }}
            >
              {count}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// Compact ledger-style strip showing live token counts.
function TokenLedger({ usage }) {
  const stats = [
    { label: "INPUT", value: usage.input },
    { label: "OUTPUT", value: usage.output },
    { label: "TOTAL", value: usage.total },
  ];

  return (
    <div
      style={{
        display: "flex",
        gap: 22,
        alignItems: "baseline",
        fontFamily: "'IBM Plex Mono', monospace",
      }}
    >
      {stats.map((s) => (
        <div key={s.label} style={{ textAlign: "right" }}>
          <div
            style={{
              fontSize: 9.5,
              letterSpacing: "0.15em",
              color: "#6f6a5e",
              marginBottom: 3,
            }}
          >
            {s.label}
          </div>
          <div
            style={{
              fontSize: 16,
              color: s.label === "TOTAL" ? "#c9933e" : "#cfc8b4",
            }}
          >
            {s.value.toLocaleString("en-IN")}
          </div>
        </div>
      ))}
    </div>
  );
}

// Masthead-style price display, sitting in the results panel above the
// Consensus Line, under its own "CURRENT PRICE — {ticker}" section label.
// Large serif number echoing the panel's other headline moments (the
// final BUY/SELL verdict), with the day-change as a small colored pill,
// rather than a small monospace data readout.
function PriceMasthead({ status, quote, ticker }) {
  if (status === "loading") {
    return (
      <div
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 13,
          color: "#b5ad97",
          letterSpacing: "0.04em",
        }}
      >
        fetching price…
      </div>
    );
  }

  if (status === "error") {
    return (
      <div
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 13,
          color: "#8c3b3b",
          letterSpacing: "0.04em",
        }}
      >
        price unavailable
      </div>
    );
  }

  if (!quote) return null;

  const change = quote.change ?? 0;
  const changePct = quote.changePercent ?? 0;
  const isUp = change >= 0;
  const colors = isUp ? VOTE_COLOR.BUY : VOTE_COLOR.SELL;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        gap: 14,
      }}
    >
      <span
        style={{
          fontFamily: "'Fraunces', serif",
          fontWeight: 600,
          fontSize: 38,
          lineHeight: 1,
          color: "#443510ff",
          letterSpacing: "-0.01em",
        }}
      >
        ₹{quote.price.toLocaleString("en-IN")}
      </span>
      <span
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 12,
          letterSpacing: "0.02em",
          color: colors.ink,
          background: colors.soft,
          borderRadius: 3,
          padding: "3px 8px",
        }}
      >
        {isUp ? "▲" : "▼"} {Math.abs(changePct).toFixed(2)}%
      </span>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Main component
// ──────────────────────────────────────────────────────────────────────────

export default function InvestmentCommittee() {
  const [ticker, setTicker] = useState("ETERNAL.NS");
  const [submittedTicker, setsubmittedTicker] = useState("ETERNAL.NS");
  const [query, setQuery] = useState("Should I buy at current levels?");

  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState(null);

  const [votesDict, setVotesDict] = useState({});
  const [final, setFinal] = useState(null);

  const [tokensByNode, setTokensByNode] = useState({});

  // Spot price — fetched independently of the SSE stream so it resolves
  // fast and isn't gated behind any analyst node finishing.
  const [priceStatus, setPriceStatus] = useState("idle"); // idle | loading | done | error
  const [quote, setQuote] = useState(null); // { price, change, changePercent }

  const abortRef = useRef(null);

  const totalUsage = useMemo(() => {
    return Object.values(tokensByNode).reduce(
      (acc, n) => ({
        input: acc.input + (n.input || 0),
        output: acc.output + (n.output || 0),
        total: acc.total + (n.total || 0),
      }),
      { input: 0, output: 0, total: 0 }
    );
  }, [tokensByNode]);

  async function fetchSpotPrice(tickerSymbol) {
    setPriceStatus("loading");
    setQuote(null);
    try {
      const res = await fetch(`${PRICE_API_URL}?ticker=${encodeURIComponent(tickerSymbol)}`);
      if (!res.ok) throw new Error(`Price fetch failed with ${res.status}`);
      const data = await res.json();
      setQuote({
        price: data.price,
        change: data.change,
        changePercent: data.changePercent,
      });
      setPriceStatus("done");
    } catch (err) {
      console.error("Spot price fetch failed:", err);
      setPriceStatus("error");
    }
  }

  async function runCommittee() {
    if (!ticker.trim() || !query.trim()) return;

    const currentTicker = ticker.trim().toUpperCase();
    setsubmittedTicker(currentTicker)

    setStatus("running");
    setErrorMessage(null);
    setVotesDict({});
    setFinal(null);
    setTokensByNode({});

    // Fire the price fetch independently — don't await it before starting
    // the analyst stream, since the two are unrelated and shouldn't block
    // each other.
    fetchSpotPrice(currentTicker);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, query }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      if (!response.body) {
        throw new Error("Streaming isn't supported in this browser/response");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let sseBuffer = "";
      const nodeBuffers = {};

      function addUsage(node, input, output, total) {
        setTokensByNode((prev) => {
          const existing = prev[node] || { input: 0, output: 0, total: 0 };
          return {
            ...prev,
            [node]: {
              input: existing.input + (input || 0),
              output: existing.output + (output || 0),
              total: existing.total + (total || 0),
            },
          };
        });
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        sseBuffer += decoder.decode(value, { stream: true });

        const events = sseBuffer.split("\n\n");
        sseBuffer = events.pop();

        for (const event of events) {
          if (!event.startsWith("data: ")) continue;

          const eventData = event.replace("data: ", "");

          try {
            const parsedSse = JSON.parse(eventData);

            if (parsedSse.type === "token" && parsedSse.content && parsedSse.node) {
              const { node, content, inputTokens, outputTokens, totalTokens } = parsedSse;

              if (!nodeBuffers[node]) nodeBuffers[node] = "";
              nodeBuffers[node] += content;

              addUsage(node, inputTokens, outputTokens, totalTokens);

              try {
                const partialData = parse(nodeBuffers[node]);

                if (node === "portfolio_manager_node") {
                  setFinal(partialData);
                } else if (AGENT_META[node]) {
                  setVotesDict((prev) => ({ ...prev, [node]: partialData }));
                }
              } catch (partialErr) {
                // Expected mid-stream: not valid (even partial) JSON yet.
              }
            } else if (parsedSse.type === "usage" && parsedSse.node) {
              const { node, inputTokens, outputTokens, totalTokens } = parsedSse;
              addUsage(node, inputTokens, outputTokens, totalTokens);
            }
          } catch (err) {
            console.error("SSE wrapper parse error:", err, eventData);
          }
        }
      }

      setStatus("done");
    } catch (error) {
      if (error.name === "AbortError") {
        setStatus("idle");
        return;
      }
      console.error("Stream failed:", error);
      setErrorMessage(
        error.message || "Couldn't reach the committee. Is the backend running?"
      );
      setStatus("error");
    } finally {
      abortRef.current = null;
    }
  }

  function cancelRun() {
    abortRef.current?.abort();
  }

  const activeVotes = Object.entries(votesDict);
  const votesArray = activeVotes.map(([, voteData]) => voteData);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0b0c0f",
        padding: "56px 24px 80px",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <link
        href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500&display=swap"
        rel="stylesheet"
      />

      <div style={{ maxWidth: 1080, margin: "0 auto" }}>
        {/* ── Header ───────────────────────────────────────────────── */}
        <header
          style={{
            marginBottom: 40,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            gap: 24,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 11,
                letterSpacing: "0.2em",
                color: "#c9933e",
                marginBottom: 10,
              }}
            >
              NSE · INDIAN EQUITIES · SIX-SEAT COMMITTEE
            </div>

            <h1
              style={{
                fontFamily: "'Fraunces', serif",
                fontWeight: 600,
                fontSize: 52,
                lineHeight: 1.04,
                color: "#f5f0e6",
                margin: 0,
                letterSpacing: "-0.01em",
              }}
            >
              The committee convenes
            </h1>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14.5,
                color: "#9a958a",
                marginTop: 12,
                maxWidth: 520,
                lineHeight: 1.6,
              }}
            >
              Six analysts research independently. Each casts a weighted vote.
              The Portfolio Manager renders the final word.
            </p>
          </div>

          {status !== "idle" && <TokenLedger usage={totalUsage} />}
        </header>

        {/* ── Input ledger row ─────────────────────────────────────── */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "200px 1fr auto",
            gap: 16,
            alignItems: "stretch",
            background: "#13141a",
            border: "1px solid #2a2b33",
            borderRadius: 4,
            padding: 16,
            marginBottom: status === "error" ? 16 : 44,
          }}
        >
          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="TICKER — e.g. TCS"
            style={{
              background: "transparent",
              border: "none",
              borderRight: "1px solid #2a2b33",
              color: "#f5f0e6",
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 14,
              letterSpacing: "0.04em",
              padding: "8px 16px 8px 4px",
              outline: "none",
            }}
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Should I buy at current levels? What's the 12-month target?"
            style={{
              background: "transparent",
              border: "none",
              color: "#f5f0e6",
              fontFamily: "'Inter', sans-serif",
              fontSize: 14,
              padding: "8px 4px",
              outline: "none",
            }}
          />
          <button
            onClick={status === "running" ? cancelRun : runCommittee}
            style={{
              background: status === "running" ? "#2a2b33" : "#c9933e",
              color: status === "running" ? "#f5f0e6" : "#1a1206",
              border: "none",
              borderRadius: 2,
              padding: "0 24px",
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 12.5,
              letterSpacing: "0.08em",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {status === "running" ? "CANCEL ✕" : "CONVENE →"}
          </button>
        </div>

        {/* ── Error banner ─────────────────────────────────────────── */}
        {status === "error" && (
          <div
            style={{
              background: "#2a1414",
              border: "1px solid #5c2b2b",
              borderRadius: 4,
              padding: "14px 18px",
              marginBottom: 44,
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 12.5,
              color: "#e8b4ab",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 16,
            }}
          >
            <span>⚠ {errorMessage}</span>
            <button
              onClick={runCommittee}
              style={{
                background: "transparent",
                border: "1px solid #8c3b3b",
                color: "#e8b4ab",
                borderRadius: 2,
                padding: "6px 14px",
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 11.5,
                letterSpacing: "0.06em",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              RETRY
            </button>
          </div>
        )}

        {/* ── Results ──────────────────────────────────────────────── */}
        {(status === "running" || status === "done") && (
          <div
            style={{
              background: "#f5f0e6",
              borderRadius: 6,
              padding: "40px 44px 48px",
            }}
          >
            <div style={{ display: "grid", gridTemplateColumns: "1.35fr 1fr", gap: 40 }}>
              <div>
                <div
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: 11,
                    letterSpacing: "0.15em",
                    color: "#a8842f",
                    marginBottom: 16,
                  }}
                >
                  ANALYST SEATS — {activeVotes.length}/6 REPORTED
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  {activeVotes.map(([nodeKey, vote]) => (
                    <AgentSeat key={nodeKey} nodeKey={nodeKey} vote={vote} status={status} />
                  ))}

                  {(status === "running" || activeVotes.length < 6) &&
                    Array.from({ length: Math.max(0, 6 - activeVotes.length) }).map((_, i) => (
                      <div
                        key={`empty-${i}`}
                        style={{
                          border: "1px dashed #d8d0ba",
                          borderRadius: 4,
                          padding: "18px 20px",
                          minHeight: 140,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontFamily: "'IBM Plex Mono', monospace",
                          fontSize: 11,
                          color: "#b5ad97",
                          letterSpacing: "0.05em",
                        }}
                      >
                        {status === "running" ? "researching…" : "awaiting seat…"}
                      </div>
                    ))}
                </div>
              </div>

              <div>
                {priceStatus !== "idle" && (
                  <div style={{ marginBottom: 28 }}>
                    <div
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: 11,
                        letterSpacing: "0.15em",
                        color: "#a8842f",
                        marginBottom: 16,
                      }}
                    >
                      CURRENT PRICE — {submittedTicker}
                    </div>
                    <PriceMasthead status={priceStatus} quote={quote} ticker={submittedTicker} />
                  </div>
                )}

                <div
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: 11,
                    letterSpacing: "0.15em",
                    color: "#a8842f",
                    marginBottom: 16,
                  }}
                >
                  CONSENSUS LINE
                </div>

                <ConsensusLine votesArray={votesArray} final={final} />

                <div
                  style={{
                    borderTop: "1px solid #d8d0ba",
                    borderBottom: final ? "3px double #c9933e" : "none",
                    marginTop: 24,
                    paddingTop: 24,
                    paddingBottom: 24,
                  }}
                >
                  {final && final.final_decision ? (
                    <>
                      <div
                        style={{
                          fontFamily: "'IBM Plex Mono', monospace",
                          fontSize: 11,
                          letterSpacing: "0.15em",
                          color: "#8a8270",
                          marginBottom: 8,
                        }}
                      >
                        PORTFOLIO MANAGER — FINAL WORD
                      </div>
                      <div
                        style={{
                          fontFamily: "'Fraunces', serif",
                          fontWeight: 600,
                          fontSize: 48,
                          color: voteColor(final.final_decision).ink,
                          lineHeight: 1,
                          marginBottom: 8,
                        }}
                      >
                        {final.final_decision}
                      </div>
                      {final.final_price_target && (
                        <div
                          style={{
                            fontFamily: "'IBM Plex Mono', monospace",
                            fontSize: 14,
                            color: "#3a362c",
                            marginBottom: 14,
                          }}
                        >
                          target ₹{final.final_price_target.toLocaleString("en-IN")}
                        </div>
                      )}
                      <p
                        style={{
                          fontFamily: "'Inter', sans-serif",
                          fontSize: 13.5,
                          lineHeight: 1.65,
                          color: "#3a362c",
                          margin: 0,
                        }}
                      >
                        {final.final_reasoning || <span style={{ opacity: 0.5 }}>Synthesizing reports...</span>}
                      </p>
                    </>
                  ) : (
                    <div
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: 12,
                        color: "#b5ad97",
                        letterSpacing: "0.04em",
                      }}
                    >
                      awaiting all seats to report…
                    </div>
                  )}
                </div>

                <div style={{ marginTop: 28 }}>
                  <div
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: 11,
                      letterSpacing: "0.15em",
                      color: "#a8842f",
                      marginBottom: 14,
                    }}
                  >
                    VOTE TALLY
                  </div>
                  <Tally votesArray={votesArray} />
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: 36,
                paddingTop: 16,
                borderTop: "1px solid #e3dcc8",
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 10.5,
                color: "#a39c89",
                letterSpacing: "0.02em",
              }}
            >
              AI-generated analysis for educational purposes only. Not financial advice.
              Consult a SEBI-registered advisor.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}