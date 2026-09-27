import os
import re
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/articles.csv"
OUTPUT_FILE = "data/analyzed_articles.csv"

COLUMNS_REQUIRED = [
    "source",
    "title",
    "url",
]


# ============================================================
# CATEGORY RULES
# ============================================================

CATEGORY_RULES = {

    "Tax": [
        r"\bskat\w*",
        r"\bskatt\w*",
        r"\bbeskat\w*",
        r"\bmoms\w*",
        r"\bafgift\w*",
        r"\btold\w*",
        r"\btax\w*",
        r"\bvat\b",
        r"\bcustoms?\b",
        r"\bimport\w*",
        r"\btransfer pricing\b",
        r"\bcbam\b",
        r"\bvida\b",
        r"\be[- ]?faktur\w*",
        r"\be[- ]?invoic\w*",
        r"\bindirect tax\w*",
        r"\bcorporate tax\w*",
    ],

    "Audit": [
        r"\brevision\w*",
        r"\brevisor\w*",
        r"\brevisionsnævn\w*",
        r"\berklæring\w*",
        r"\berklær\w*",
        r"\baudit\w*",
        r"\bauditor\w*",
        r"\bassurance\b",
        r"\bkontrolstandard\w*",
        r"\brevisionsstandard\w*",
        r"\bisa\b",
    ],

    "Finance & CFO": [
        r"\bcfo\b",
        r"\bfinance\b",
        r"\bfinancial\w*",
        r"\bfinans\w*",
        r"\bregnskab\w*",
        r"\bårsrapport\w*",
        r"\bbudget\w*",
        r"\bforecast\w*",
        r"\bøkonomi\w*",
        r"\bøkonomisk\w*",
        r"\brapportering\w*",
        r"\breporting\b",

        # Accounting / reporting standards
        r"\bifrs\b",
        r"\bias\b",
        r"\biasb\b",
        r"\baccounting\b",
        r"\baccounting standard\w*",
        r"\bfinancial statement\w*",
        r"\bfinancial reporting standard\w*",

        # ESG / sustainability reporting
        r"\besrs\b",
        r"\bcsrd\b",
        r"\besg\b",
        r"\bbæredygtighed\w*",
        r"\bsustainability\w*",

        # Finance transformation
        r"\berp\b",
        r"\bcontrolling\b",
        r"\bcontroller\w*",
        r"\bcash flow\b",
        r"\blikviditet\w*",
    ],

    "AI & Technology": [
        r"\bai\b",
        r"\bai act\b",
        r"\bkunstig intelligens\b",
        r"\bartificial intelligence\b",
        r"\bgenerative ai\b",
        r"\bgenai\b",
        r"\bmachine learning\b",
        r"\bdeepfake\w*",
        r"\bautomatisering\w*",
        r"\bautomation\b",
        r"\bdigitalisering\w*",
        r"\bdigital transformation\b",
        r"\bcyber\w*",
        r"\bdatasikkerhed\w*",
        r"\bdata governance\b",
        r"\bdigital\w*",
        r"\bteknologi\w*",
        r"\btechnology\b",
    ],
}


# ============================================================
# TREND RULES
# ============================================================

TREND_RULES = {

    "AI governance & regulation": [
        r"\bai act\b",
        r"\bai governance\b",
        r"\bai regulation\b",
        r"\bkunstig intelligens\b",
        r"\bforbudt\w* ai\b",
        r"\bdeepfake\w*",
        r"\bai[- ]?regulering\w*",
    ],

    "AI adoption & automation": [
        r"\bgenerative ai\b",
        r"\bgenai\b",
        r"\bautomation\b",
        r"\bautomatisering\w*",
        r"\bmachine learning\b",
    ],

    "Digital tax & e-invoicing": [
        r"\be[- ]?faktur\w*",
        r"\be[- ]?invoic\w*",
        r"\bdigital tax\b",
        r"\bvida\b",
        r"\bvat in the digital age\b",
    ],

    "VAT & indirect tax": [
        r"\bmoms\w*",
        r"\bvat\b",
        r"\bindirect tax\w*",
        r"\bafgift\w*",
    ],

    "Corporate tax": [
        r"\bcorporate tax\w*",
        r"\bselskabsskat\w*",
        r"\bbeskat\w*",
        r"\bskatt\w*",
        r"\bskat\w*",
    ],

    "Customs & trade": [
        r"\btold\w*",
        r"\bcustoms?\b",
        r"\bcbam\b",
        r"\bimport\w*",
    ],

    "Audit & assurance": [
        r"\brevision\w*",
        r"\brevisor\w*",
        r"\baudit\w*",
        r"\bassurance\b",
        r"\berklæring\w*",
    ],

    "Sustainability reporting": [
        r"\besg\b",
        r"\bcsrd\b",
        r"\besrs\b",
        r"\bbæredygtighed\w*",
        r"\bsustainability reporting\b",
    ],

    "Financial reporting": [
        r"\bfinancial reporting\b",
        r"\bfinancial statement\w*",
        r"\bfinancial reporting standard\w*",
        r"\baccounting\b",
        r"\baccounting standard\w*",
        r"\bifrs\b",
        r"\bias\b",
        r"\biasb\b",
        r"\bregnskab\w*",
        r"\bårsrapport\w*",
        r"\brapportering\w*",
    ],

    "Finance transformation": [
        r"\bcfo\b",
        r"\bfinance transformation\b",
        r"\berp\b",
        r"\bforecast\w*",
        r"\bcontrolling\b",
        r"\bautomatisering\w*",
    ],

    "Cyber & data governance": [
        r"\bcyber\w*",
        r"\bdatasikkerhed\w*",
        r"\bdata governance\b",
    ],
}


# ============================================================
# OBVIOUS NOISE
# ============================================================

NOISE_PATTERNS = [
    r"^spring hovednavigationen over$",
    r"^skip to main content$",
    r"^skip navigation$",
    r"^kontakt os$",
    r"^contact us$",
    r"^cookie settings$",
    r"^privacy policy$",
    r"^privatlivspolitik$",
    r"^tilbage$",
    r"^back$",
    r"^menu$",
    r"^søg$",
    r"^search$",
]


# ============================================================
# TEXT CLEANING
# ============================================================

def fix_encoding(text):

    if pd.isna(text):
        return ""

    text = str(text)

    suspicious = [
        "Ã",
        "Â",
        "â€",
        "ðŸ",
    ]

    if any(
        marker in text
        for marker in suspicious
    ):

        try:
            text = (
                text
                .encode("latin1")
                .decode("utf-8")
            )

        except (
            UnicodeEncodeError,
            UnicodeDecodeError,
        ):
            pass

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def normalize_text(text):

    return fix_encoding(
        text
    ).lower().strip()


# ============================================================
# NOISE DETECTION
# ============================================================

def is_noise(title):

    text = normalize_text(title)

    if not text:
        return True

    for pattern in NOISE_PATTERNS:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            return True

    return False


# ============================================================
# MATCHING
# ============================================================

def find_matches(
    text,
    patterns,
):

    matches = []

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            matches.append(
                pattern
            )

    return matches


# ============================================================
# CATEGORY CLASSIFICATION
# ============================================================

def classify_categories(title):

    text = normalize_text(title)

    results = {}

    for (
        category,
        patterns,
    ) in CATEGORY_RULES.items():

        matches = find_matches(
            text,
            patterns,
        )

        if matches:

            results[
                category
            ] = matches

    if not results:

        return (
            "Unclassified",
            "",
            0,
        )

    sorted_categories = sorted(
        results.items(),
        key=lambda item: len(
            item[1]
        ),
        reverse=True,
    )

    primary_category = (
        sorted_categories[0][0]
    )

    all_categories = " | ".join(
        category
        for category, _
        in sorted_categories
    )

    total_matches = sum(
        len(matches)
        for matches
        in results.values()
    )

    return (
        primary_category,
        all_categories,
        total_matches,
    )


# ============================================================
# TREND CLASSIFICATION
# ============================================================

def classify_trend(title):

    text = normalize_text(title)

    results = {}

    for (
        trend,
        patterns,
    ) in TREND_RULES.items():

        matches = find_matches(
            text,
            patterns,
        )

        if matches:

            results[trend] = len(
                matches
            )

    if not results:

        return "Unclassified"

    return max(
        results,
        key=results.get,
    )


# ============================================================
# RELEVANCE SCORE
#
# Internal Communication Monitor score.
# Not an external benchmark.
# ============================================================

def calculate_relevance(
    match_count,
    trend,
):

    if match_count == 0:
        return 0.0

    score = 4.0

    score += min(
        match_count,
        4,
    ) * 1.0

    if trend != "Unclassified":
        score += 1.0

    return min(
        round(
            score,
            1,
        ),
        10.0,
    )


# ============================================================
# STATUS
#
# Relevant = classified with sufficient evidence
# Review   = uncertain, but retained
# Noise    = navigation / technical content
# ============================================================

def determine_status(
    noise,
    category,
    relevance,
):

    if noise:
        return "Noise"

    if (
        category != "Unclassified"
        and relevance >= 5
    ):
        return "Relevant"

    return "Review"


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_articles():

    if not os.path.exists(
        INPUT_FILE
    ):

        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist. "
            "Run collector.py first."
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    for column in COLUMNS_REQUIRED:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: "
                f"{column}"
            )

    # Clean encoding
    df["title"] = (
        df["title"]
        .apply(fix_encoding)
    )

    df["source"] = (
        df["source"]
        .apply(fix_encoding)
    )

    rows = []

    for _, row in df.iterrows():

        title = row["title"]

        noise = is_noise(
            title
        )

        if noise:

            primary_category = "Noise"
            categories = "Noise"
            match_count = 0
            trend = "Noise"
            relevance = 0.0
            status = "Noise"

        else:

            (
                primary_category,
                categories,
                match_count,
            ) = classify_categories(
                title
            )

            trend = classify_trend(
                title
            )

            relevance = (
                calculate_relevance(
                    match_count,
                    trend,
                )
            )

            status = (
                determine_status(
                    noise,
                    primary_category,
                    relevance,
                )
            )

        result = row.to_dict()

        result.update({
            "status":
                status,

            "primary_category":
                primary_category,

            "categories":
                categories,

            "keyword_matches":
                match_count,

            "trend":
                trend,

            "relevance":
                relevance,
        })

        rows.append(
            result
        )

    analyzed_df = pd.DataFrame(
        rows
    )

    # ========================================================
    # SORT
    # Relevant first → Review → Noise
    # ========================================================

    status_order = {
        "Relevant": 0,
        "Review": 1,
        "Noise": 2,
    }

    analyzed_df[
        "_status_order"
    ] = (
        analyzed_df["status"]
        .map(status_order)
    )

    analyzed_df = (
        analyzed_df
        .sort_values(
            by=[
                "_status_order",
                "relevance",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )

    analyzed_df = (
        analyzed_df
        .drop(
            columns=[
                "_status_order"
            ]
        )
    )

    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(
        "data",
        exist_ok=True,
    )

    analyzed_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ========================================================
    # REPORT
    # ========================================================

    print(
        f"\nAnalyzed "
        f"{len(analyzed_df)} "
        f"articles."
    )

    print(
        "\nStatus:"
    )

    for (
        status,
        count,
    ) in (
        analyzed_df["status"]
        .value_counts()
        .items()
    ):

        print(
            f"  {status}: "
            f"{count}"
        )

    relevant_df = (
        analyzed_df[
            analyzed_df["status"]
            == "Relevant"
        ]
    )

    print(
        "\nRelevant articles "
        "by primary category:"
    )

    if relevant_df.empty:

        print(
            "  No relevant "
            "articles detected."
        )

    else:

        for (
            category,
            count,
        ) in (
            relevant_df[
                "primary_category"
            ]
            .value_counts()
            .items()
        ):

            print(
                f"  {category}: "
                f"{count}"
            )

    review_count = (
        analyzed_df["status"]
        == "Review"
    ).sum()

    print(
        f"\nArticles kept "
        f"for review: "
        f"{review_count}"
    )

    print(
        f"\nSaved analysis to "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    analyze_articles()
