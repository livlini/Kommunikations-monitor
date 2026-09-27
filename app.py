import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Communication Monitor",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Communication Monitor")
st.caption("Weekly intelligence for Finance & CFO · Audit · Tax · AI & Technology")

# -------------------------------------------------------------------
# TREND SCORE
# -------------------------------------------------------------------
# Scoren er transparent og beregnes ud fra fire komponenter:
#
# 1) Omtale:      1 point pr. relevant signal/artikel, maks. 30 point
# 2) Vækst:       100 % vækst eller mere = 30 point.
#                 Fx 50 % vækst = 15 point. Negativ vækst = 0 point.
# 3) Kildebredde: 2 point pr. unik kilde, maks. 20 point
# 4) Relevans:    Gennemsnitlig relevans 0-10 ganget med 2,
#                 maks. 20 point
#
# Maksimal samlet score = 100 point.
#
# VIGTIGT:
# Dette er vores egen indikator for styrken af et trendsignal.
# Det er ikke en ekstern eller etableret branchemåling.

def calculate_trend_score(signals, previous_signals, sources, relevance):
    volume_points = min(signals, 30)

    if previous_signals > 0:
        growth_pct = ((signals - previous_signals) / previous_signals) * 100
    else:
        growth_pct = 100 if signals > 0 else 0

    growth_points = min(max(growth_pct, 0) / 100 * 30, 30)
    source_points = min(sources * 2, 20)
    relevance_points = min(max(relevance, 0), 10) * 2

    total = volume_points + growth_points + source_points + relevance_points

    return {
        "score": round(total),
        "growth_pct": growth_pct,
        "volume_points": round(volume_points, 1),
        "growth_points": round(growth_points, 1),
        "source_points": round(source_points, 1),
        "relevance_points": round(relevance_points, 1),
    }


# Prototype-data.
# Når den automatiske collector kobles på, erstattes disse tal af ugens faktiske data.
DATA = [
    {
        "Trend": "AI governance & AI Act",
        "Category": "AI & Technology",
        "Signals": 18,
        "PreviousSignals": 13,
        "Sources": 5,
        "Relevance": 9.0,
        "Why": "Regulation and governance are moving from principles into operational compliance and supervision.",
        "Angle": "What should CFOs have in place before scaling AI across finance?",
        "Format": "LinkedIn · Event · Newsletter",
    },
    {
        "Trend": "AI in the finance function",
        "Category": "Finance & CFO",
        "Signals": 16,
        "PreviousSignals": 12,
        "Sources": 4,
        "Relevance": 8.8,
        "Why": "AI is increasingly discussed as a finance transformation tool rather than a standalone technology experiment.",
        "Angle": "From AI pilots to measurable value in the finance function.",
        "Format": "LinkedIn · Article",
    },
    {
        "Trend": "Audit standards & assurance",
        "Category": "Audit",
        "Signals": 12,
        "PreviousSignals": 11,
        "Sources": 3,
        "Relevance": 7.8,
        "Why": "Professional guidance and standards continue to change, creating a need for concise client communication.",
        "Angle": "Three assurance developments finance leaders should know this quarter.",
        "Format": "Newsletter · Article",
    },
    {
        "Trend": "Digital tax & e-invoicing",
        "Category": "Tax",
        "Signals": 10,
        "PreviousSignals": 9,
        "Sources": 4,
        "Relevance": 8.2,
        "Why": "Tax reporting is becoming increasingly digital and data-driven, affecting processes and controls.",
        "Angle": "Is your finance function ready for increasingly digital tax reporting?",
        "Format": "Event · LinkedIn",
    },
    {
        "Trend": "Finance automation",
        "Category": "Finance & CFO",
        "Signals": 9,
        "PreviousSignals": 8,
        "Sources": 4,
        "Relevance": 7.5,
        "Why": "Automation remains central to productivity, forecasting and operating-model discussions in finance.",
        "Angle": "Where should a CFO automate first?",
        "Format": "LinkedIn · Newsletter",
    },
]

# Beregn score og uge-til-uge-vækst automatisk.
for item in DATA:
    result = calculate_trend_score(
        item["Signals"],
        item["PreviousSignals"],
        item["Sources"],
        item["Relevance"],
    )
    item.update(result)

df = pd.DataFrame(DATA)

with st.sidebar:
    st.header("Monitor settings")
    categories = st.multiselect(
        "Categories",
        ["Finance & CFO", "Audit", "Tax", "AI & Technology"],
        default=["Finance & CFO", "Audit", "Tax", "AI & Technology"],
    )

    st.markdown("**Keywords**")
    st.caption(
        "AI agents · generative AI · AI governance · CFO · finance transformation · "
        "forecasting · ERP · audit · assurance · revision · tax · VAT · "
        "transfer pricing · e-invoicing"
    )

    st.divider()
    st.caption(
        "Prototype-data vises i denne version. Scoren beregnes nu automatisk "
        "ud fra de viste inputdata."
    )

view = df[df["Category"].isin(categories)].sort_values("score", ascending=False)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active trends", len(view))
c2.metric("Signals analysed", int(view["Signals"].sum()) if len(view) else 0)
c3.metric("Source coverage", int(view["Sources"].max()) if len(view) else 0)
c4.metric("Last refresh", str(date.today()))

with st.expander("ℹ️ Hvad betyder Trend Strength?"):
    st.markdown(
        """
**Trend Strength (0–100)** er vores egen transparente indikator for, hvor stærkt
et trendsignal er i de kilder, monitoren følger. Det er **ikke** en ekstern
branchemåling.

Scoren består af fire dele:

| Faktor | Beregning | Maks. |
|---|---|---:|
| **Omtale** | 1 point pr. relevant signal/artikel | 30 |
| **Vækst** | 100 % vækst eller mere = 30 point; 50 % = 15 point | 30 |
| **Kildebredde** | 2 point pr. unik kilde | 20 |
| **Relevans** | Gennemsnitlig relevans (0–10) × 2 | 20 |
| **Total** | Summen af de fire dele | **100** |

Et *signal* er i prototypen en relevant artikel eller publicering, som matcher
monitorens emne og kriterier.
"""
    )

st.subheader("Emerging trends")

for _, row in view.iterrows():
    with st.container(border=True):
        a, b, c = st.columns([5, 1.2, 1.2])

        a.markdown(f"### {row['Trend']}")
        a.caption(
            f"{row['Category']} · {row['Signals']} signals · "
            f"{row['Sources']} sources · relevance {row['Relevance']:.1f}/10"
        )

        b.metric("Trend Strength", f"{int(row['score'])}/100")
        c.metric("WoW", f"{row['growth_pct']:+.0f}%")

        st.write(row["Why"])
        st.markdown(f"**Communication opportunity:** {row['Angle']}")
        st.caption(f"Suggested format: {row['Format']}")

        with st.expander("Se beregningen"):
            st.write(
                f"**Omtale:** {int(row['Signals'])} signaler → "
                f"**{row['volume_points']:.1f}/30 point**"
            )
            st.write(
                f"**Vækst:** {int(row['PreviousSignals'])} → {int(row['Signals'])} signaler "
                f"({row['growth_pct']:+.1f} %) → **{row['growth_points']:.1f}/30 point**"
            )
            st.write(
                f"**Kildebredde:** {int(row['Sources'])} unikke kilder × 2 → "
                f"**{row['source_points']:.1f}/20 point**"
            )
            st.write(
                f"**Relevans:** {row['Relevance']:.1f}/10 × 2 → "
                f"**{row['relevance_points']:.1f}/20 point**"
            )
            st.divider()
            st.markdown(f"### Samlet Trend Strength: {int(row['score'])}/100")

st.subheader("Trend overview")
if len(view):
    st.bar_chart(view.set_index("Trend")["score"])
else:
    st.info("Vælg mindst én kategori i menuen.")

st.subheader("Source universe")
st.markdown(
    """
- **KPMG Denmark Insights** — AI & Data, Audit & Assurance, Corporate Tax, Market Trends
- **FSR – danske revisorer** — audit, accounting, tax and industry updates
- **Skattestyrelsen** — tax news and official updates
- **Digitaliseringsstyrelsen** — AI regulation, supervision and digitalisation
- Extendable with additional public RSS/API sources
"""
)

st.subheader("How the weekly engine works")
st.code(
    """1. Fetch new public articles / RSS entries
2. Deduplicate and keyword-filter
3. Classify: Finance & CFO / Audit / Tax / AI & Technology
4. Extract topic + audience + communication angle
5. Aggregate topics and compare with prior weeks
6. Calculate transparent Trend Strength score
7. Publish the new dashboard snapshot""",
    language="text",
)
