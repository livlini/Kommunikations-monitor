import os
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
# GENERAL DESIGN
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
# DATA CHECK
# ============================================================

if trends.empty:

    st.warning(
        "No trend data is available yet. "
        "Run the Weekly Data Collection workflow "
        "to generate data/trends.csv."
    )

    st.stop()


# Only trends active in the latest monitored week

active_trends = trends[
    trends["signals"] > 0
].copy()

active_trends = active_trends.sort_values(
    "trend_strength",
    ascending=False,
)


if active_trends.empty:

    st.info(
        "No active trends were detected "
        "in the latest monitored week."
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
        Trendscore is the combined trend strength
        based on four different factors.
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
        Hover over a card to see the calculation
        behind its Trend Strength.
    </div>
    """,
    unsafe_allow_html=True,
)


# Maximum 6 strongest trends

card_data = (
    active_trends
    .head(6)
    .reset_index(drop=True)
)


# ============================================================
# HELPERS
# ============================================================

def format_wow(value):

    if value > 0:
        return f"+{value:.1f}%"

    if value < 0:
        return f"{value:.1f}%"

    return "0.0%"


def safe_text(value):

    return html.escape(
        str(value)
    )


# ============================================================
# FLIP CARD
# ============================================================

def render_flip_card(row):

    category = safe_text(
        row["category"]
    )

    trend = safe_text(
        row["trend"]
    )

    wow = format_wow(
        row["wow_growth_pct"]
    )

    signals = int(
        row["signals"]
    )

    sources = int(
        row["sources"]
    )

    strength = float(
        row["trend_strength"]
    )

    volume_points = float(
        row["volume_points"]
    )

    growth_points = float(
        row["growth_points"]
    )

    source_points = float(
        row["source_points"]
    )

    relevance_points = float(
        row["relevance_points"]
    )

    average_relevance = float(
        row["average_relevance"]
    )


    card_html = f"""
    <!DOCTYPE html>

    <html>

    <head>

    <style>

        * {{
            box-sizing: border-box;
        }}

        html,
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Helvetica,
                Arial,
                sans-serif;
        }}


        .flip-card {{
            background-color: transparent;
            width: 100%;
            height: 300px;
            perspective: 1200px;
            cursor: pointer;
        }}


        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 100%;

            transition:
                transform 0.65s
                cubic-bezier(
                    0.4,
                    0.2,
                    0.2,
                    1
                );

            transform-style: preserve-3d;
        }}


        .flip-card:hover
        .flip-card-inner {{

            transform:
                rotateY(180deg);
        }}


        .flip-card-front,
        .flip-card-back {{

            position: absolute;

            width: 100%;
            height: 100%;

            top: 0;
            left: 0;

            border-radius: 18px;

            padding: 28px;

            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;

            box-shadow:
                0 6px 18px
                rgba(
                    22,
                    61,
                    115,
                    0.08
                );
        }}


        .flip-card-front {{

            background: #ffffff;

            border:
                1px solid
                #e3eaf3;
        }}


        .flip-card-back {{

            background:
                #163d73;

            color:
                #ffffff;

            transform:
                rotateY(180deg);

            border:
                1px solid
                #163d73;
        }}


        .category {{

            color:
                #6282ad;

            font-size:
                12px;

            font-weight:
                700;

            text-transform:
                uppercase;

            letter-spacing:
                0.8px;

            margin-bottom:
                12px;
        }}


        .trend {{

            color:
                #163d73;

            font-size:
                23px;

            line-height:
                1.25;

            font-weight:
                700;

            min-height:
                60px;
        }}


        .strength-label {{

            color:
                #7a8797;

            font-size:
                12px;

            font-weight:
                600;

            letter-spacing:
                0.5px;

            margin-top:
                22px;
        }}


        .strength {{

            color:
                #163d73;

            font-size:
                52px;

            line-height:
                1;

            font-weight:
                750;

            margin-top:
                5px;
        }}


        .out-of {{

            color:
                #98a2b3;

            font-size:
                16px;

            font-weight:
                500;
        }}


        .metrics {{

            color:
                #667085;

            font-size:
                14px;

            margin-top:
                17px;
        }}


        .back-title {{

            font-size:
                21px;

            font-weight:
                700;

            margin-bottom:
                19px;
        }}


        .score-row {{

            display:
                flex;

            justify-content:
                space-between;

            align-items:
                center;

            padding:
                7px 0;

            font-size:
                14px;

            border-bottom:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    0.10
                );
        }}


        .score-value {{

            font-weight:
                700;
        }}


        .detail {{

            margin-top:
                14px;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.75
                );

            font-size:
                12px;

            line-height:
                1.5;
        }}


        .total {{

            display:
                flex;

            justify-content:
                space-between;

            margin-top:
                15px;

            padding-top:
                13px;

            border-top:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    0.35
                );

            font-size:
                15px;

            font-weight:
                700;
        }}

    </style>

    </head>


    <body>


        <div class="flip-card">

            <div class="flip-card-inner">


                <!-- FRONT -->

                <div class="flip-card-front">

                    <div class="category">
                        {category}
                    </div>

                    <div class="trend">
                        {trend}
                    </div>

                    <div class="strength-label">
                        TREND STRENGTH
                    </div>

                    <div class="strength">

                        {strength:.1f}

                        <span class="out-of">
                            / 100
                        </span>

                    </div>

                    <div class="metrics">

                        WoW:
                        {wow}

                        &nbsp; · &nbsp;

                        {signals}
                        signals

                        &nbsp; · &nbsp;

                        {sources}
                        sources

                    </div>

                </div>


                <!-- BACK -->

                <div class="flip-card-back">

                    <div class="back-title">
                        Score calculation
                    </div>


                    <div class="score-row">

                        <span>
                            Volume
                        </span>

                        <span class="score-value">
                            {volume_points:.1f} / 30
                        </span>

                    </div>


                    <div class="score-row">

                        <span>
                            Growth
                        </span>

                        <span class="score-value">
                            {growth_points:.1f} / 30
                        </span>

                    </div>


                    <div class="score-row">

                        <span>
                            Source breadth
                        </span>

                        <span class="score-value">
                            {source_points:.1f} / 20
                        </span>

                    </div>


                    <div class="score-row">

                        <span>
                            Relevance
                        </span>

                        <span class="score-value">
                            {relevance_points:.1f} / 20
                        </span>

                    </div>


                    <div class="detail">

                        {signals} relevant signals
                        · {sources} unique sources

                        <br>

                        Average relevance:
                        {average_relevance:.1f} / 10

                        <br>

                        Week-over-week:
                        {wow}

                    </div>


                    <div class="total">

                        <span>
                            Trend Strength
                        </span>

                        <span>
                            {strength:.1f} / 100
                        </span>

                    </div>


                </div>


            </div>

        </div>


    </body>

    </html>
    """


    components.html(
        card_html,
        height=320,
        scrolling=False,
    )


# ============================================================
# CARD GRID
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

        render_flip_card(
            card_data.iloc[i]
        )


    if i + 1 < len(card_data):

        with col2:

            render_flip_card(
                card_data.iloc[
                    i + 1
                ]
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
        Public sources currently represented
        in the monitored dataset.
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

        source_name = html.escape(
            str(
                row["source"]
            )
        )

        st.markdown(
            f"""
            <div class="source-box">

                <div class="source-name">
                    {source_name}
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
# ABOUT
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

The monitor is intended as a communication and market-monitoring tool rather than an external statistical benchmark.
        """
    )
