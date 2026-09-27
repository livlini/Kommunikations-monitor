import streamlit as st
import pandas as pd
import html

st.set_page_config(page_title="Communication Monitor", page_icon="◫", layout="wide")

# ---------- Scoring ----------
def calculate_trend_score(signals, previous_signals, sources, relevance):
    volume = min(signals, 30)
    growth_pct = ((signals - previous_signals) / previous_signals * 100) if previous_signals > 0 else (100 if signals > 0 else 0)
    growth = min(max(growth_pct, 0) / 100 * 30, 30)
    breadth = min(sources * 2, 20)
    relevance_pts = min(max(relevance, 0), 10) * 2
    return {
        "score": round(volume + growth + breadth + relevance_pts),
        "growth_pct": growth_pct,
        "volume_points": volume,
        "growth_points": growth,
        "source_points": breadth,
        "relevance_points": relevance_pts,
    }

DATA = [
    {"Trend":"AI governance & AI Act","Category":"AI & Technology","Signals":18,"PreviousSignals":13,"Sources":5,"Relevance":9.0,
     "Why":"Regulation and governance are moving from principles into operational compliance and supervision."},
    {"Trend":"AI in the finance function","Category":"Finance & CFO","Signals":16,"PreviousSignals":12,"Sources":4,"Relevance":8.8,
     "Why":"AI is increasingly discussed as a finance transformation tool rather than a standalone technology experiment."},
    {"Trend":"Audit standards & assurance","Category":"Audit","Signals":12,"PreviousSignals":11,"Sources":3,"Relevance":7.8,
     "Why":"Professional guidance and standards continue to change, creating a need for concise client communication."},
    {"Trend":"Digital tax & e-invoicing","Category":"Tax","Signals":10,"PreviousSignals":9,"Sources":4,"Relevance":8.2,
     "Why":"Tax reporting is becoming increasingly digital and data-driven, affecting processes and controls."},
]

for d in DATA:
    d.update(calculate_trend_score(d["Signals"], d["PreviousSignals"], d["Sources"], d["Relevance"]))

df = pd.DataFrame(DATA)

# ---------- Styling ----------
st.markdown("""
<style>
:root { --blue:#164a7b; --blue2:#2d6ea3; --pale:#eef4f8; --line:#d8e2ea; --ink:#17324a; }
.stApp { background:#f6f8fa; color:var(--ink); }
.block-container { max-width:1180px; padding-top:2.1rem; padding-bottom:3rem; }
h1,h2,h3 { color:#123d63 !important; }
[data-testid="stHeader"] { background:rgba(246,248,250,.94); }
[data-testid="stSidebar"] { display:none; }

.hero {background:white;border:1px solid var(--line);border-radius:18px;padding:28px 32px;margin-bottom:24px;}
.eyebrow {font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#5f7890;font-weight:700;}
.hero h1 {margin:.2rem 0 .25rem 0;font-size:2.25rem;}
.hero p {margin:0;color:#6a7e90;}

.flip-grid {display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:18px 0 34px;}
.flip-card {height:270px;perspective:1200px;}
.flip-inner {position:relative;width:100%;height:100%;transition:transform .65s;transform-style:preserve-3d;}
.flip-card:hover .flip-inner {transform:rotateY(180deg);}
.flip-front,.flip-back {
 position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;
 border-radius:18px;border:1px solid #d5e0e8;background:white;box-shadow:0 5px 18px rgba(28,65,96,.06);
 padding:26px;box-sizing:border-box;
}
.flip-front {display:flex;flex-direction:column;justify-content:space-between;}
.flip-back {transform:rotateY(180deg);background:#eef4f8;overflow:auto;}
.category {font-size:.78rem;text-transform:uppercase;letter-spacing:.11em;color:#668198;font-weight:700;}
.trend-name {font-size:1.45rem;font-weight:750;color:#173f62;line-height:1.2;margin-top:8px;}
.metrics {display:flex;gap:38px;}
.metric-label {font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#7890a3;}
.metric-value {font-size:2rem;font-weight:750;color:#164a7b;}
.back-title {font-size:1.05rem;font-weight:750;color:#164a7b;margin-bottom:10px;}
.desc {font-size:.91rem;line-height:1.45;color:#425d73;margin-bottom:13px;}
.calc {font-size:.82rem;line-height:1.6;color:#536c80;}
.calc strong {color:#173f62;}
.source-box {background:white;border:1px solid var(--line);border-radius:18px;padding:24px 28px;margin-top:10px;}
.source-box p {color:#5f7486;margin-bottom:0;}
.note {font-size:.86rem;color:#647d91;margin:.4rem 0 1rem;}
@media(max-width:800px){.flip-grid{grid-template-columns:1fr}.flip-card{height:290px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Weekly communication intelligence</div>
  <h1>Communication Monitor</h1>
  <p>Emerging signals across Finance & CFO, Audit, Tax and AI & Technology.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Chart first ----------
st.subheader("Trend Strength Overview")
chart = df[["Trend","score"]].set_index("Trend")
st.bar_chart(chart, horizontal=True, height=300)

st.markdown('<div class="note"><b>Trendscore is the combined trend strength based on four different factors.</b></div>', unsafe_allow_html=True)

with st.expander("How is the Trend Strength calculated?"):
    st.markdown("""
The score ranges from **0 to 100** and is calculated using four transparent factors:

| Factor | Calculation | Maximum |
|---|---|---:|
| **Volume** | 1 point per relevant signal/article | 30 points |
| **Growth** | 100% growth or more = 30 points; 50% growth = 15 points | 30 points |
| **Source breadth** | 2 points per unique source | 20 points |
| **Relevance** | Average relevance score (0–10) × 2 | 20 points |
| **Total** | Sum of the four factors | **100 points** |

The Trend Strength is an internal indicator designed for this monitor. It is not an external industry benchmark.
""")

# ---------- 2x2 flip cards ----------
st.subheader("Areas")
cards = []
for d in sorted(DATA, key=lambda x: x["score"], reverse=True):
    name = html.escape(d["Trend"])
    category = html.escape(d["Category"])
    why = html.escape(d["Why"])
    cards.append(f"""
    <div class="flip-card">
      <div class="flip-inner">
        <div class="flip-front">
          <div>
            <div class="category">{category}</div>
            <div class="trend-name">{name}</div>
          </div>
          <div class="metrics">
            <div><div class="metric-label">Trend Strength</div><div class="metric-value">{d["score"]}/100</div></div>
            <div><div class="metric-label">WoW</div><div class="metric-value">{d["growth_pct"]:+.0f}%</div></div>
          </div>
        </div>
        <div class="flip-back">
          <div class="back-title">{name}</div>
          <div class="desc">{why}</div>
          <div class="calc">
            <strong>Calculation</strong><br>
            Volume: {d["Signals"]} signals → {d["volume_points"]:.1f}/30<br>
            Growth: {d["PreviousSignals"]} → {d["Signals"]} ({d["growth_pct"]:+.1f}%) → {d["growth_points"]:.1f}/30<br>
            Source breadth: {d["Sources"]} sources × 2 → {d["source_points"]:.1f}/20<br>
            Relevance: {d["Relevance"]:.1f}/10 × 2 → {d["relevance_points"]:.1f}/20<br>
            <strong>Total: {d["score"]}/100</strong>
          </div>
        </div>
      </div>
    </div>""")

st.markdown('<div class="flip-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)

# ---------- Sources retained ----------
st.subheader("Sources")
st.markdown("""
<div class="source-box">
<b>KPMG Denmark Insights</b> — AI & Data, Audit & Assurance, Corporate Tax and Market Trends.<br><br>
<b>FSR – danske revisorer</b> — audit, accounting, tax and industry updates.<br><br>
<b>Skattestyrelsen</b> — tax news and official updates.<br><br>
<b>Digitaliseringsstyrelsen</b> — AI regulation, supervision and digitalisation.<br><br>
<b>Additional public sources</b> — the source universe can be extended with relevant public RSS/API sources.
<p>Prototype data is still used in this version. Live weekly collection can be connected as the next step.</p>
</div>
""", unsafe_allow_html=True)
df = pd.DataFrame(DATA)

# ---------- Styling ----------
st.markdown("""
<style>
:root { --blue:#164a7b; --blue2:#2d6ea3; --pale:#eef4f8; --line:#d8e2ea; --ink:#17324a; }
.stApp { background:#f6f8fa; color:var(--ink); }
.block-container { max-width:1180px; padding-top:2.1rem; padding-bottom:3rem; }
h1,h2,h3 { color:#123d63 !important; }
[data-testid="stHeader"] { background:rgba(246,248,250,.94); }
[data-testid="stSidebar"] { display:none; }

.hero {background:white;border:1px solid var(--line);border-radius:18px;padding:28px 32px;margin-bottom:24px;}
.eyebrow {font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#5f7890;font-weight:700;}
.hero h1 {margin:.2rem 0 .25rem 0;font-size:2.25rem;}
.hero p {margin:0;color:#6a7e90;}

.flip-grid {display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:18px 0 34px;}
.flip-card {height:270px;perspective:1200px;}
.flip-inner {position:relative;width:100%;height:100%;transition:transform .65s;transform-style:preserve-3d;}
.flip-card:hover .flip-inner {transform:rotateY(180deg);}
.flip-front,.flip-back {
 position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;
 border-radius:18px;border:1px solid #d5e0e8;background:white;box-shadow:0 5px 18px rgba(28,65,96,.06);
 padding:26px;box-sizing:border-box;
}
.flip-front {display:flex;flex-direction:column;justify-content:space-between;}
.flip-back {transform:rotateY(180deg);background:#eef4f8;overflow:auto;}
.category {font-size:.78rem;text-transform:uppercase;letter-spacing:.11em;color:#668198;font-weight:700;}
.trend-name {font-size:1.45rem;font-weight:750;color:#173f62;line-height:1.2;margin-top:8px;}
.metrics {display:flex;gap:38px;}
.metric-label {font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#7890a3;}
.metric-value {font-size:2rem;font-weight:750;color:#164a7b;}
.back-title {font-size:1.05rem;font-weight:750;color:#164a7b;margin-bottom:10px;}
.desc {font-size:.91rem;line-height:1.45;color:#425d73;margin-bottom:13px;}
.calc {font-size:.82rem;line-height:1.6;color:#536c80;}
.calc strong {color:#173f62;}
.source-box {background:white;border:1px solid var(--line);border-radius:18px;padding:24px 28px;margin-top:10px;}
.source-box p {color:#5f7486;margin-bottom:0;}
.note {font-size:.86rem;color:#647d91;margin:.4rem 0 1rem;}
@media(max-width:800px){.flip-grid{grid-template-columns:1fr}.flip-card{height:290px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Weekly communication intelligence</div>
  <h1>Communication Monitor</h1>
  <p>Emerging signals across Finance & CFO, Audit, Tax and AI & Technology.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Chart first ----------
st.subheader("Trend Strength Overview")

import altair as alt

chart = alt.Chart(df).mark_bar(
    size=42,
    cornerRadiusEnd=5
).encode(
    x=alt.X(
        "score:Q",
        title="Trend Strength",
        scale=alt.Scale(domain=[0, 100])
    ),
    y=alt.Y(
        "Trend:N",
        title=None,
        sort="-x"
    ),
    tooltip=[
        alt.Tooltip("Trend:N", title="Trend"),
        alt.Tooltip("score:Q", title="Trend Strength")
    ]
)

labels = alt.Chart(df).mark_text(
    align="left",
    baseline="middle",
    dx=8,
    fontSize=14,
    fontWeight="bold"
).encode(
    x="score:Q",
    y=alt.Y("Trend:N", sort="-x"),
    text=alt.Text("score:Q")
)

st.altair_chart(
    chart + labels,
    use_container_width=True
)

st.markdown('<div class="note"><b>Trendscore is the combined trend strength based on four different factors.</b></div>', unsafe_allow_html=True)

with st.expander("How is the Trend Strength calculated?"):
    st.markdown("""
The score ranges from **0 to 100** and is calculated using four transparent factors:

| Factor | Calculation | Maximum |
|---|---|---:|
| **Volume** | 1 point per relevant signal/article | 30 points |
| **Growth** | 100% growth or more = 30 points; 50% growth = 15 points | 30 points |
| **Source breadth** | 2 points per unique source | 20 points |
| **Relevance** | Average relevance score (0–10) × 2 | 20 points |
| **Total** | Sum of the four factors | **100 points** |

The Trend Strength is an internal indicator designed for this monitor. It is not an external industry benchmark.
""")

# ---------- 2x2 flip cards ----------
st.subheader("Areas")
cards = []
for d in sorted(DATA, key=lambda x: x["score"], reverse=True):
    name = html.escape(d["Trend"])
    category = html.escape(d["Category"])
    why = html.escape(d["Why"])
    cards.append(f"""
    <div class="flip-card">
      <div class="flip-inner">
        <div class="flip-front">
          <div>
            <div class="category">{category}</div>
            <div class="trend-name">{name}</div>
          </div>
          <div class="metrics">
            <div><div class="metric-label">Trend Strength</div><div class="metric-value">{d["score"]}/100</div></div>
            <div><div class="metric-label">WoW</div><div class="metric-value">{d["growth_pct"]:+.0f}%</div></div>
          </div>
        </div>
        <div class="flip-back">
          <div class="back-title">{name}</div>
          <div class="desc">{why}</div>
          <div class="calc">
            <strong>Calculation</strong><br>
            Volume: {d["Signals"]} signals → {d["volume_points"]:.1f}/30<br>
            Growth: {d["PreviousSignals"]} → {d["Signals"]} ({d["growth_pct"]:+.1f}%) → {d["growth_points"]:.1f}/30<br>
            Source breadth: {d["Sources"]} sources × 2 → {d["source_points"]:.1f}/20<br>
            Relevance: {d["Relevance"]:.1f}/10 × 2 → {d["relevance_points"]:.1f}/20<br>
            <strong>Total: {d["score"]}/100</strong>
          </div>
        </div>
      </div>
    </div>""")

st.markdown('<div class="flip-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)

# ---------- Sources retained ----------
st.subheader("Sources")
st.markdown("""
<div class="source-box">
<b>KPMG Denmark Insights</b> — AI & Data, Audit & Assurance, Corporate Tax and Market Trends.<br><br>
<b>FSR – danske revisorer</b> — audit, accounting, tax and industry updates.<br><br>
<b>Skattestyrelsen</b> — tax news and official updates.<br><br>
<b>Digitaliseringsstyrelsen</b> — AI regulation, supervision and digitalisation.<br><br>
<b>Additional public sources</b> — the source universe can be extended with relevant public RSS/API sources.
<p>Prototype data is still used in this version. Live weekly collection can be connected as the next step.</p>
</div>
""", unsafe_allow_html=True)
