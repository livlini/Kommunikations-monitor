import os
from datetime import datetime, timezone

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/analyzed_articles.csv"
OUTPUT_FILE = "data/trends.csv"

REQUIRED_COLUMNS = [
    "source",
    "title",
    "published_date",
    "status",
    "primary_category",
    "trend",
    "relevance",
]


# ============================================================
# TREND STRENGTH
#
# Maximum = 100 points
#
# Volume         max 30
# Growth         max 30
# Source breadth max 20
# Relevance      max 20
#
# This is an internal Communication Monitor indicator.
# It is not an external industry benchmark.
# ============================================================

def calculate_trend_strength(
    signals,
    previous_signals,
    sources,
    relevance,
):

    # --------------------------------------------------------
    # 1. VOLUME — MAX 30
    # --------------------------------------------------------

    volume_points = min(
        signals,
        30,
    )

    # --------------------------------------------------------
    # 2. WEEK-OVER-WEEK GROWTH — MAX 30
    # --------------------------------------------------------

    if previous_signals > 0:

        growth_pct = (
            (
                signals
                - previous_signals
            )
            / previous_signals
        ) * 100

    elif signals > 0:

        # New trend with no signals in previous week.
        growth_pct = 100

    else:

        growth_pct = 0

    # Negative growth does not subtract points.
    growth_points = min(
        max(
            growth_pct,
            0,
        )
        / 100
        * 30,
        30,
    )

    # --------------------------------------------------------
    # 3. SOURCE BREADTH — MAX 20
    #
    # 2 points per unique source.
    # --------------------------------------------------------

    source_points = min(
        sources * 2,
        20,
    )

    # --------------------------------------------------------
    # 4. RELEVANCE — MAX 20
    #
    # Analyzer relevance is 0–10.
    # --------------------------------------------------------

    relevance_points = min(
        max(
            relevance,
            0,
        ),
        10,
    ) * 2

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total = (
        volume_points
        + growth_points
        + source_points
        + relevance_points
    )

    return {
        "trend_strength": round(
            total,
            1,
        ),

        "volume_points": round(
            volume_points,
            1,
        ),

        "growth_points": round(
            growth_points,
            1,
        ),

        "source_points": round(
            source_points,
            1,
        ),

        "relevance_points": round(
            relevance_points,
            1,
        ),

        "wow_growth_pct": round(
            growth_pct,
            1,
        ),
    }


# ============================================================
# LOAD DATA
# ============================================================

def load_articles():

    if not os.path.exists(
        INPUT_FILE
    ):

        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist. "
            "Run analyzer.py first."
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: "
                f"{column}"
            )

    return df


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_articles(df):

    # Only articles that Analyzer classified
    # as relevant may affect Trend Strength.
    df = df[
        df["status"]
        == "Relevant"
    ].copy()

    # Unclassified trends cannot be scored.
    df = df[
        df["trend"]
        != "Unclassified"
    ].copy()

    # Convert publication date.
    df["published_date"] = pd.to_datetime(
        df["published_date"],
        errors="coerce",
        utc=True,
    )

    # Articles without a valid publication date
    # cannot be used for weekly comparisons.
    missing_dates = (
        df["published_date"]
        .isna()
        .sum()
    )

    if missing_dates:

        print(
            f"WARNING: "
            f"{missing_dates} relevant articles "
            f"have no valid published_date "
            f"and will not be used "
            f"in weekly trend calculations."
        )

    df = df.dropna(
        subset=[
            "published_date"
        ]
    )

    df["relevance"] = pd.to_numeric(
        df["relevance"],
        errors="coerce",
    ).fillna(0)

    return df


# ============================================================
# DEFINE WEEK WINDOWS
#
# We use the newest publication date in the dataset as the
# reference point. This is useful for historical/testing data
# and avoids pretending older data belongs to the current week.
# ============================================================

def get_week_windows(df):

    if df.empty:
        return None

    newest_date = (
        df["published_date"]
        .max()
        .normalize()
    )

    # Monday of the week containing newest_date
    current_week_start = (
        newest_date
        - pd.Timedelta(
            days=newest_date.weekday()
        )
    )

    current_week_end = (
        current_week_start
        + pd.Timedelta(
            days=7
        )
    )

    previous_week_start = (
        current_week_start
        - pd.Timedelta(
            days=7
        )
    )

    previous_week_end = (
        current_week_start
    )

    return {
        "current_start":
            current_week_start,

        "current_end":
            current_week_end,

        "previous_start":
            previous_week_start,

        "previous_end":
            previous_week_end,
    }


# ============================================================
# BUILD TREND DATA
# ============================================================

def build_trends(
    df,
    windows,
):

    current_df = df[
        (
            df["published_date"]
            >= windows["current_start"]
        )
        &
        (
            df["published_date"]
            < windows["current_end"]
        )
    ].copy()

    previous_df = df[
        (
            df["published_date"]
            >= windows["previous_start"]
        )
        &
        (
            df["published_date"]
            < windows["previous_end"]
        )
    ].copy()

    # Include trends observed in either week.
    all_trends = sorted(
        set(
            current_df["trend"]
            .dropna()
            .tolist()
        )
        |
        set(
            previous_df["trend"]
            .dropna()
            .tolist()
        )
    )

    rows = []

    for trend in all_trends:

        current_trend = current_df[
            current_df["trend"]
            == trend
        ]

        previous_trend = previous_df[
            previous_df["trend"]
            == trend
        ]

        signals = len(
            current_trend
        )

        previous_signals = len(
            previous_trend
        )

        unique_sources = (
            current_trend["source"]
            .nunique()
        )

        if signals > 0:

            average_relevance = (
                current_trend[
                    "relevance"
                ]
                .mean()
            )

            primary_category = (
                current_trend[
                    "primary_category"
                ]
                .mode()
                .iloc[0]
            )

        else:

            # Trend only existed in previous week.
            average_relevance = 0

            if not previous_trend.empty:

                primary_category = (
                    previous_trend[
                        "primary_category"
                    ]
                    .mode()
                    .iloc[0]
                )

            else:

                primary_category = (
                    "Unclassified"
                )

        score = (
            calculate_trend_strength(
                signals,
                previous_signals,
                unique_sources,
                average_relevance,
            )
        )

        rows.append({
            "trend":
                trend,

            "category":
                primary_category,

            "signals":
                signals,

            "previous_signals":
                previous_signals,

            "wow_growth_pct":
                score[
                    "wow_growth_pct"
                ],

            "sources":
                unique_sources,

            "average_relevance":
                round(
                    average_relevance,
                    1,
                ),

            "volume_points":
                score[
                    "volume_points"
                ],

            "growth_points":
                score[
                    "growth_points"
                ],

            "source_points":
                score[
                    "source_points"
                ],

            "relevance_points":
                score[
                    "relevance_points"
                ],

            "trend_strength":
                score[
                    "trend_strength"
                ],
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# MAIN
# ============================================================

def run_trend_engine():

    print(
        "\n================================"
    )

    print(
        "Communication Monitor "
        "Trend Engine"
    )

    print(
        "================================"
    )

    df = load_articles()

    df = prepare_articles(
        df
    )

    if df.empty:

        print(
            "\nNo dated relevant articles "
            "available for trend calculation."
        )

        # Still create a valid empty file.
        pd.DataFrame(
            columns=[
                "trend",
                "category",
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
        ).to_csv(
            OUTPUT_FILE,
            index=False,
        )

        return

    windows = get_week_windows(
        df
    )

    print(
        "\nCurrent week:"
    )

    print(
        f"  "
        f"{windows['current_start'].date()} "
        f"to "
        f"{(windows['current_end'] - pd.Timedelta(days=1)).date()}"
    )

    print(
        "\nPrevious week:"
    )

    print(
        f"  "
        f"{windows['previous_start'].date()} "
        f"to "
        f"{(windows['previous_end'] - pd.Timedelta(days=1)).date()}"
    )

    trends_df = build_trends(
        df,
        windows,
    )

    if not trends_df.empty:

        trends_df = (
            trends_df
            .sort_values(
                by="trend_strength",
                ascending=False,
            )
        )

    os.makedirs(
        "data",
        exist_ok=True,
    )

    trends_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"\nCalculated "
        f"{len(trends_df)} trends."
    )

    if not trends_df.empty:

        print(
            "\nTrend Strength:"
        )

        for _, row in (
            trends_df.iterrows()
        ):

            print(
                f"  "
                f"{row['trend']}: "
                f"{row['trend_strength']} "
                f"| signals "
                f"{row['signals']} "
                f"| previous "
                f"{row['previous_signals']} "
                f"| sources "
                f"{row['sources']}"
            )

    print(
        f"\nSaved trends to "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    run_trend_engine()
