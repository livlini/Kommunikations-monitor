import os
import re
import pandas as pd


INPUT_FILE = "data/articles.csv"
OUTPUT_FILE = "data/analyzed_articles.csv"

CATEGORIES = {
    "AI & Technology": [
        "artificial intelligence", "ai ", " ai", "kunstig intelligens",
        "ai act", "deepfake", "deepfakes", "digitalisering",
        "cyber", "data", "automation", "automatisering",
        "digital transformation", "teknologi"
    ],

    "Tax": [
        "tax", "skat", "moms", "vat", "customs", "told",
        "transfer pricing", "e-invoicing", "e-invoice",
        "e-fakturering", "taxation", "cbam"
    ],

    "Audit": [
        "audit", "auditing", "revision", "revisor",
        "assurance", "erklæring", "erklæringer",
        "revisionsstandard", "revisionsstandarder"
    ],

    "Finance & CFO": [
        "cfo", "finance", "financial reporting", "regnskab",
        "årsrapport", "ifrs", "esrs", "csrd",
        "sustainability reporting", "bæredygtighedsrapportering",
        "forecast", "forecasting", "budget",
        "erp", "controlling"
    ],
}


TREND_RULES = {
    "AI governance & regulation": [
        "ai act", "ai regulation", "ai governance",
        "kunstig intelligens", "forbudt ai",
        "deepfake", "deepfakes"
    ],

    "Digital tax & e-invoicing": [
        "e-invoicing", "e-invoice", "e-fakturering",
        "digital tax", "vida", "vat in the digital age"
    ],

    "VAT & indirect tax": [
        "vat", "moms", "indirect tax"
    ],

    "Audit & assurance": [
        "audit", "revision", "revisor",
        "assurance", "erklæring", "erklæringer"
    ],

    "Sustainability reporting": [
        "esg", "csrd", "esrs",
        "sustainability reporting",
        "bæredygtighed", "bæredygtighedsrapportering"
    ],

    "Financial reporting": [
        "financial reporting", "ifrs",
        "årsrapport", "regnskab"
    ],

    "Finance transformation": [
        "finance transformation", "cfo",
        "automation", "automatisering",
        "erp", "forecasting"
    ],
}


NOISE_PHRASES = [
    "spring hovednavigationen over",
    "skip to main content",
    "cookie",
    "privacy policy",
    "kontakt os",
    "contact us",
    "læs mere",
    "read more",
]


def fix_encoding(text):
    """
    Attempts to repair common UTF-8/mojibake problems,
    e.g. bÃ¦redygtighed -> bæredygtighed.
    """
    if pd.isna(text):
        return ""

    text = str(text)

    if any(marker in text for marker in ["Ã", "Â", "â€"]):
        try:
            text = text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    return re.sub(r"\s+", " ", text).strip()


def is_noise(title):
    """Remove obvious navigation/system content."""
    title_lower = title.lower().strip()

    if len(title_lower) < 12:
        return True

    for phrase in NOISE_PHRASES:
        if phrase in title_lower:
            return True

    return False


def keyword_matches(text, keywords):
    """Return the keywords found in a text."""
    text = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in text
    ]


def classify_category(title):
    """
    Find the category with the strongest keyword match.
    """
    scores = {}

    for category, keywords in CATEGORIES.items():
        matches = keyword_matches(title, keywords)
        scores[category] = len(matches)

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Other", 0

    return best_category, scores[best_category]


def classify_trend(title):
    """
    Assign a more specific communication trend.
    """
    scores = {}

    for trend, keywords in TREND_RULES.items():
        matches = keyword_matches(title, keywords)
        scores[trend] = len(matches)

    best_trend = max(scores, key=scores.get)

    if scores[best_trend] == 0:
        return "Other"

    return best_trend


def calculate_relevance(category_matches, trend):
    """
    Transparent first-pass relevance score.

    0 = no detected relevance
    10 = strong match

    This is an internal Communication Monitor score,
    not an external benchmark.
    """
    if category_matches == 0:
        return 0.0

    score = 4.0

    score += min(category_matches, 3) * 1.5

    if trend != "Other":
        score += 1.5

    return min(round(score, 1), 10.0)


def analyze_articles():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist. Run collector.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = ["source", "title", "url"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    # Fix text encoding
    df["title"] = df["title"].apply(fix_encoding)
    df["source"] = df["source"].apply(fix_encoding)

    # Identify obvious noise
    df["is_noise"] = df["title"].apply(is_noise)

    categories = []
    match_counts = []
    trends = []
    relevance_scores = []

    for _, row in df.iterrows():
        title = row["title"]

        if row["is_noise"]:
            categories.append("Noise")
            match_counts.append(0)
            trends.append("Noise")
            relevance_scores.append(0.0)
            continue

        category, match_count = classify_category(title)
        trend = classify_trend(title)

        relevance = calculate_relevance(
            match_count,
            trend
        )

        categories.append(category)
        match_counts.append(match_count)
        trends.append(trend)
        relevance_scores.append(relevance)

    df["category"] = categories
    df["keyword_matches"] = match_counts
    df["trend"] = trends
    df["relevance"] = relevance_scores

    # Relevant means we detected a category
    # and the row was not navigation/noise.
    df["relevant"] = (
        (~df["is_noise"])
        & (df["category"] != "Other")
        & (df["relevance"] > 0)
    )

    os.makedirs("data", exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Analyzed {len(df)} articles."
    )

    print(
        f"Relevant: {df['relevant'].sum()}"
    )

    print(
        f"Noise: {df['is_noise'].sum()}"
    )

    print("\nRelevant articles by category:")

    relevant_df = df[df["relevant"]]

    if relevant_df.empty:
        print("  No relevant articles detected.")
    else:
        for category, count in (
            relevant_df["category"]
            .value_counts()
            .items()
        ):
            print(f"  {category}: {count}")

    print(
        f"\nSaved results to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    analyze_articles()
