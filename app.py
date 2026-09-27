import os
import pandas as pd
import streamlit as st
import altair as alt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Communication Monitor",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# FILES
# ============================================================

TREND_FILE = "data/trends.csv"
ARTICLE_FILE = "data/analyzed_articles.csv"


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f7fa;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: #163d73;
    }

    .main-title {
        font-size: 42px;
        font-weight: 750;
        color: #163d73;
        margin-bottom: 0px;
    }

    .subtitle {
        color: #667085;
        font-size: 17px;
        margin-top: 4px;
        margin-bottom: 32px;
    }

    .section-title {
        color: #163d73;
        font-size: 25px;
        font-weight: 700;
        margin-top: 32px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #667085;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .trend-card {
        background: white;
        border: 1px solid #e3eaf3;
        border-radius: 18px;
        padding: 27px;
        min-height: 225px;
        box-shadow: 0 6px 18px rgba(22, 61, 115, 0.07);
        margin-bottom: 10px;
    }

    .category-label {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #6282ad;
        margin-bottom: 10px;
    }

    .trend-name {
        color: #163d73;
        font-size: 22px;
        line-height: 1.25;
        font-weight: 700;
        min-height: 55px;
    }

    .strength-label {
        color: #7a8797;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.4px;
        margin-top: 20px;
    }

    .strength-number {
        color: #163d73;
        font-size: 48px;
        font-weight: 750;
        line-height: 1.05;
        margin-top: 3px;
    }

    .strength-max {
        color: #98a2b3;
        font-size: 16px;
        font-weight: 500;
    }

    .metrics-line {
        color: #667085;
        font-size: 14px;
        margin-top: 14px;
    }

    .source-box {
        background: white;
        border: 1px solid #e3eaf3;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 10px;
    }

    .source-name {
        color: #163d73;
        font-weight: 650;
        font-size: 15px;
    }

    .source-count {
        color: #667085;
        font-size: 13px;
        margin-top: 3px;
    }

    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid #e3eaf3;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_trends():

    if not os.path.exists(TREND_FILE):
        return pd.DataFrame()

    df = pd.read_csv(TREND_FILE)

    numeric_columns = [
        "signals",
        "previous_signals",
        "wow_growth_pct",
        "sources",
        "average_relevance",
        "volume_points",
        "growth_points",
        "source_points",
        "relevance_points",
        "trend_strength",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0)

    return df


@st.cache_data
def load_articles():

    if not os.path.exists(ARTICLE_FILE):
        return pd.DataFrame()

    return pd.read_csv(ARTICLE_FILE)


trends = load_trends()
articles = load_articles()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Communication Monitor</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        A weekly signal monitor tracking communication-relevant
        developments across Finance & CFO, Audit, Tax and AI & Technology.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHECK DATA
# ============================================================

if trends.empty:

    st.warning(
        "No trend data is available yet. "
        "Run the Weekly Data Collection workflow to generate data/trends.csv."
    )

    st.stop()


# Only show trends with signals in the latest monitored week

active_trends = trends[
    trends["signals"] > 0
].copy()

active_trends = active_trends.sort_values(
    "trend_strength",
    ascending=False,
)


if active_trends.empty:

    st.info(
        "No active trends were detected in the latest monitored week."
    )

    st.stop()


# ============================================================
# TREND STRENGTH OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Trend Strength Overview</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Trendscore is the combined trend strength based on four different factors.
    </div>
    """,
    unsafe_allow_html=True,
)


chart_data = active_trends[
    [
        "trend",
        "trend_strength",
        "signals",
        "wow_growth_pct",
        "sources",
        "average_relevance",
    ]
].copy()


chart = (
    alt.Chart(chart_data)
    .mark_bar(
        cornerRadiusTopRight=6,
        cornerRadiusBottomRight=6,
        color="#7ea6d8",
    )
    .encode(

        y=alt.Y(
            "trend:N",
            sort="-x",
            title=None,
            axis=alt.Axis(
                labelLimit=350,
                labelFontSize=13,
            ),
        ),

        x=alt.X(
            "trend_strength:Q",
            title="Trend Strength",
            scale=alt.Scale(
                domain=[0, 100]
            ),
        ),

        tooltip=[
            alt.Tooltip(
                "trend:N",
                title="Trend",
            ),
            alt.Tooltip(
                "trend_strength:Q",
                title="Trend Strength",
                format=".1f",
            ),
            alt.Tooltip(
                "signals:Q",
                title="Signals",
            ),
            alt.Tooltip(
                "wow_growth_pct:Q",
                title="WoW",
                format=".1f",
            ),
            alt.Tooltip(
                "sources:Q",
                title="Sources",
            ),
            alt.Tooltip(
                "average_relevance:Q",
                title="Avg. relevance",
                format=".1f",
            ),
        ],
    )
    .properties(
        height=max(
            280,
            len(chart_data) * 48,
        )
    )
)


st.altair_chart(
    chart,
    use_container_width=True,
)


# ============================================================
# SCORE EXPLANATION
# ============================================================

with st.expander(
    "How is Trend Strength calculated?"
):

    st.markdown(
        """
**Trend Strength is an internal indicator from 0–100.**

It combines four factors:

- **Volume — max 30 points:** 1 point per relevant signal/article.
- **Week-over-week growth — max 30 points:** compares the latest monitored week with the previous week. +100% or more gives 30 points.
- **Source breadth — max 20 points:** 2 points per unique source.
- **Relevance — max 20 points:** average relevance score from 0–10, multiplied by 2.

The score is designed specifically for this Communication Monitor and is **not an external industry benchmark**.
        """
    )


# ============================================================
# CURRENT TRENDS
# ============================================================

st.markdown(
    '<div class="section-title">Current Trends</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Strongest communication-relevant signals detected in the latest monitored week.
    </div>
    """,
    unsafe_allow_html=True,
)


# Maximum six cards

card_data = (
    active_trends
    .head(6)
    .reset_index(drop=True)
)


def format_wow(value):

    if value > 0:
        return f"+{value:.1f}%"

    if value < 0:
        return f"{value:.1f}%"

    return "0.0%"


def render_card(row):

    wow = format_wow(
        row["wow_growth_pct"]
    )

    st.markdown(
        f"""
        <div class="trend-card">

            <div class="category-label">
                {row["category"]}
            </div>

            <div class="trend-name">
                {row["trend"]}
            </div>

            <div class="strength-label">
                TREND STRENGTH
            </div>

            <div class="strength-number">
                {row["trend_strength"]:.1f}
                <span class="strength-max">
                    / 100
                </span>
            </div>

            <div class="metrics-line">
                WoW: {wow}
                &nbsp;&nbsp;·&nbsp;&nbsp;
                {int(row["signals"])} signals
                &nbsp;&nbsp;·&nbsp;&nbsp;
                {int(row["sources"])} sources
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "Show calculation"
    ):

        st.markdown(
            f"""
**Volume:** {row["volume_points"]:.1f} / 30  
{int(row["signals"])} relevant signals in the latest monitored week.

**Growth:** {row["growth_points"]:.1f} / 30  
WoW change: **{wow}**

**Source breadth:** {row["source_points"]:.1f} / 20  
{int(row["sources"])} unique sources.

**Relevance:** {row["relevance_points"]:.1f} / 20  
Average relevance: **{row["average_relevance"]:.1f} / 10**

---

**Trend Strength: {row["trend_strength"]:.1f} / 100**
            """
        )


# ============================================================
# 2 x 2 / 2-COLUMN LAYOUT
# ============================================================

for i in range(
    0,
    len(card_data),
    2,
):

    col1, col2 = st.columns(
        2,
        gap="large",
    )

    with col1:
        render_card(
            card_data.iloc[i]
        )

    if i + 1 < len(card_data):

        with col2:
            render_card(
                card_data.iloc[i + 1]
            )


# ============================================================
# SOURCES
# ============================================================

st.markdown(
    '<div class="section-title">Sources</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Public sources currently represented in the monitored dataset.
    </div>
    """,
    unsafe_allow_html=True,
)


if (
    not articles.empty
    and "source" in articles.columns
):

    source_counts = (
        articles["source"]
        .value_counts()
        .reset_index()
    )

    source_counts.columns = [
        "source",
        "articles",
    ]

    for _, row in source_counts.iterrows():

        st.markdown(
            f"""
            <div class="source-box">

                <div class="source-name">
                    {row["source"]}
                </div>

                <div class="source-count">
                    {int(row["articles"])}
                    collected articles
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

else:

    st.write(
        "Source information is not available."
    )


# ============================================================
# METHODOLOGY
# ============================================================

with st.expander(
    "About the monitor"
):

    st.markdown(
        """
The Communication Monitor collects publicly available articles from selected professional and regulatory sources.

**1. Collector**  
Collects article titles, publication dates, URLs and sources.

**2. Analyzer**  
Uses transparent rule-based classification to identify relevant categories, trends and an internal relevance score.

**3. Trend Engine**  
Compares the latest monitored week with the previous week and calculates Trend Strength from volume, growth, source breadth and relevance.

Articles classified as **Review**, **Noise**, or with an **Unclassified trend** do not contribute to Trend Strength.

The Communication Monitor is intended as a communication and market-monitoring tool rather than an external statistical benchmark.
        """
    )
