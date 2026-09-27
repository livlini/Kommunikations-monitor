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
        margin-top: 30px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #667085;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* FLIP CARD */

    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 290px;
        perspective: 1000px;
        margin-bottom: 22px;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.65s;
        transform-style: preserve-3d;
    }

    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }

    .flip-card-front,
    .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;

        border-radius: 18px;
        padding: 27px;

        box-sizing: border-box;

        box-shadow:
            0 6px 18px
            rgba(22, 61, 115, 0.08);
    }

    .flip-card-front {
        background: white;
        border: 1px solid #e3eaf3;
    }

    .flip-card-back {
        background: #163d73;
        color: white;
        transform: rotateY(180deg);
    }

    .category-label {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        color: #6282ad;
        margin-bottom: 10px;
    }

    .trend-name {
        color: #163d73;
        font-size: 22px;
        line-height: 1.25;
        font-weight: 700;
        min-height: 58px;
    }

    .strength-label {
        color: #7a8797;
        font-size: 13px;
        margin-top: 25px;
    }

    .strength-number {
        color: #163d73;
        font-size: 52px;
        font-weight: 750;
        line-height: 1;
        margin-top: 4px;
    }

    .wow {
        margin-top: 16px;
        font-size: 14px;
        color: #667085;
    }

    .back-title {
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .back-line {
        font-size: 14px;
        margin-bottom: 9px;
        opacity: 0.95;
    }

    .back-total {
        margin-top: 15px;
        padding-top: 13px;
        border-top: 1px solid rgba(255,255,255,0.3);
        font-size: 15px;
        font-weight: 700;
    }

    .source-box {
        background: white;
        border: 1px solid #e3eaf3;
        border-radius: 14px;
        padding: 20px 24px;
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
# NO DATA
# ============================================================

if trends.empty:

    st.warning(
        "No trend data is available yet. "
        "Run the Weekly Data Collection workflow to generate data/trends.csv."
    )

    st.stop()


# ============================================================
# REMOVE TRENDS WITH NO CURRENT SIGNALS
#
# Previous-week trends remain in trends.csv for calculation
# purposes, but the dashboard focuses on active current trends.
# ============================================================

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
        - **Week-over-week growth — max 30 points:** measures growth compared with the previous week. +100% or more gives 30 points.
        - **Source breadth — max 20 points:** 2 points per unique source.
        - **Relevance — max 20 points:** average relevance score from 0–10, multiplied by 2.

        The score is designed for this Communication Monitor and is
        **not an external industry benchmark**.
        """
    )


# ============================================================
# TREND CARDS
# ============================================================

st.markdown(
    '<div class="section-title">Current Trends</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-description">
        Hover over a trend to see the calculation behind its Trend Strength.
    </div>
    """,
    unsafe_allow_html=True,
)


# Show maximum 6 strongest current trends
card_data = active_trends.head(6).reset_index(
    drop=True
)


def format_wow(value):

    if value > 0:
        return f"+{value:.1f}%"

    if value < 0:
        return f"{value:.1f}%"

    return "0.0%"


def trend_card(row):

    wow = format_wow(
        row["wow_growth_pct"]
    )

    html = f"""
    <div class="flip-card">
        <div class="flip-card-inner">

            <div class="flip-card-front">

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
                </div>

                <div class="wow">
                    WoW: {wow}
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    {int(row["signals"])} signals
                </div>

            </div>


            <div class="flip-card-back">

                <div class="back-title">
                    Score calculation
                </div>

                <div class="back-line">
                    Volume:
                    <strong>
                    {row["volume_points"]:.1f} / 30
                    </strong>
                </div>

                <div class="back-line">
                    Growth:
                    <strong>
                    {row["growth_points"]:.1f} / 30
                    </strong>
                </div>

                <div class="back-line">
                    Source breadth:
                    <strong>
                    {row["source_points"]:.1f} / 20
                    </strong>
                </div>

                <div class="back-line">
                    Relevance:
                    <strong>
                    {row["relevance_points"]:.1f} / 20
                    </strong>
                </div>

                <div class="back-line">
                    Unique sources:
                    <strong>
                    {int(row["sources"])}
                    </strong>
                </div>

                <div class="back-line">
                    Avg. relevance:
                    <strong>
                    {row["average_relevance"]:.1f} / 10
                    </strong>
                </div>

                <div class="back-total">
                    Total Trend Strength:
                    {row["trend_strength"]:.1f} / 100
                </div>

            </div>

        </div>
    </div>
    """

    return html


# 2-column card layout
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

        st.markdown(
            trend_card(
                card_data.iloc[i]
            ),
            unsafe_allow_html=True,
        )

    if i + 1 < len(card_data):

        with col2:

            st.markdown(
                trend_card(
                    card_data.iloc[i + 1]
                ),
                unsafe_allow_html=True,
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
        Public sources currently represented in the analyzed dataset.
    </div>
    """,
    unsafe_allow_html=True,
)


if not articles.empty and "source" in articles.columns:

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
                    {int(row["articles"])} collected articles
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
        The Communication Monitor collects publicly available
        articles from selected professional and regulatory sources.

        The pipeline consists of three stages:

        **1. Collector**  
        Collects article titles, publication dates, URLs and sources.

        **2. Analyzer**  
        Uses transparent rule-based classification to identify
        relevant categories, trends and an internal relevance score.

        **3. Trend Engine**  
        Compares the latest monitored week with the previous week
        and calculates Trend Strength from volume, growth,
        source breadth and relevance.

        Articles classified as **Review**, **Noise** or with an
        **Unclassified trend** do not contribute to Trend Strength.

        The monitor is intended as a communication and market
        monitoring tool rather than an external statistical benchmark.
        """
    )
