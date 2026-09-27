import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "CommunicationMonitor/2.0 "
        "(student research project; public web content)"
    )
}

TIMEOUT = 30
REQUEST_DELAY = 1

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "articles.csv")

COLUMNS = [
    "source",
    "title",
    "url",
    "published_date",
    "collected_at",
]


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(text):
    """Remove unnecessary whitespace."""
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def fetch_page(url):
    """Download one public webpage."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    response.raise_for_status()

    time.sleep(REQUEST_DELAY)

    return BeautifulSoup(response.text, "html.parser")


def normalize_url(base_url, href):
    """Convert relative URLs to absolute URLs."""
    if not href:
        return ""

    return urljoin(base_url, href)


def parse_date(text):
    """
    Try to convert common Danish and European
    date formats into YYYY-MM-DD.
    """

    if not text:
        return ""

    text = clean_text(text)

    # Remove common prefixes
    text = re.sub(
        r"(?i)publiceret\s*:?\s*",
        "",
        text,
    )

    text = re.sub(
        r"(?i)publication date\s*:?\s*",
        "",
        text,
    )

    # Danish month names
    danish_months = {
        "januar": "January",
        "februar": "February",
        "marts": "March",
        "april": "April",
        "maj": "May",
        "juni": "June",
        "juli": "July",
        "august": "August",
        "september": "September",
        "oktober": "October",
        "november": "November",
        "december": "December",
    }

    translated = text.lower()

    for dk, en in danish_months.items():
        translated = translated.replace(dk, en)

    formats = [
        "%d.%m.%Y",
        "%d.%m.%y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
    ]

    for date_format in formats:
        try:
            parsed = datetime.strptime(
                translated.strip(),
                date_format,
            )

            return parsed.strftime("%Y-%m-%d")

        except ValueError:
            continue

    # Search inside a longer string
    numeric_match = re.search(
        r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b",
        text,
    )

    if numeric_match:
        day, month, year = numeric_match.groups()

        if len(year) == 2:
            year = "20" + year

        try:
            parsed = datetime(
                int(year),
                int(month),
                int(day),
            )

            return parsed.strftime("%Y-%m-%d")

        except ValueError:
            pass

    return ""


def find_date_near_element(element):
    """
    Search the surrounding article/card for a date.
    """

    containers = [
        element,
        element.parent,
        element.parent.parent if element.parent else None,
    ]

    date_patterns = [
        r"\d{1,2}\.\d{1,2}\.\d{2,4}",
        r"\d{1,2}\s+[A-Za-zÆØÅæøå]+\s+\d{4}",
    ]

    for container in containers:

        if container is None:
            continue

        text = clean_text(
            container.get_text(" ", strip=True)
        )

        for pattern in date_patterns:
            match = re.search(pattern, text)

            if match:
                parsed = parse_date(match.group())

                if parsed:
                    return parsed

    return ""


def create_article(
    source,
    title,
    url,
    published_date="",
):
    """Create a standardized article record."""

    return {
        "source": source,
        "title": clean_text(title),
        "url": url,
        "published_date": published_date,
        "collected_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def valid_article(article):
    """Basic quality control."""

    if not article["title"]:
        return False

    if len(article["title"]) < 12:
        return False

    if not article["url"]:
        return False

    return True


# ============================================================
# 1. DIGITALISERINGSSTYRELSEN
# ============================================================

def collect_digst():

    source = "Digitaliseringsstyrelsen"

    base_url = "https://digst.dk"

    archive_url = (
        "https://digst.dk/nyheder/nyhedsarkiv/"
    )

    print(f"\nCollecting: {source}")

    soup = fetch_page(archive_url)

    articles = []

    for link in soup.find_all("a", href=True):

        href = link.get("href", "")
        title = clean_text(
            link.get_text(" ", strip=True)
        )

        # Individual DIGST news articles generally
        # sit below /nyheder/nyhedsarkiv/YYYY/
        if not re.search(
            r"/nyheder/nyhedsarkiv/\d{4}/",
            href,
        ):
            continue

        url = normalize_url(
            base_url,
            href,
        )

        published_date = find_date_near_element(
            link
        )

        article = create_article(
            source,
            title,
            url,
            published_date,
        )

        if valid_article(article):
            articles.append(article)

    print(
        f"{source}: {len(articles)} articles found"
    )

    return articles


# ============================================================
# 2. ERHVERVSSTYRELSEN
# ============================================================

def collect_erhvervsstyrelsen():

    source = "Erhvervsstyrelsen"
    base_url = "https://erhvervsstyrelsen.dk"
    news_url = "https://erhvervsstyrelsen.dk/nyheder"

    print(f"\nCollecting: {source}")

    soup = fetch_page(news_url)

    articles = []
    seen_urls = set()

    # Find all links on the official news page
    for link in soup.find_all("a", href=True):

        href = link.get("href", "")
        title = clean_text(
            link.get_text(" ", strip=True)
        )

        if not title:
            continue

        url = normalize_url(base_url, href)
        parsed = urlparse(url)

        # Only keep Erhvervsstyrelsen links
        if parsed.netloc not in [
            "erhvervsstyrelsen.dk",
            "www.erhvervsstyrelsen.dk",
        ]:
            continue

        # Skip obvious navigation/system pages
        ignored_paths = {
            "",
            "/",
            "/nyheder",
            "/kontakt",
            "/om-os",
            "/soeg",
            "/publikationer",
        }

        if parsed.path.rstrip("/") in ignored_paths:
            continue

        # Skip duplicate URLs
        if url in seen_urls:
            continue

        # News cards contain a date in their surrounding content.
        published_date = find_date_near_element(link)

        # Additional search higher up in the card structure
        if not published_date:
            parent = link

            for _ in range(5):
                parent = getattr(parent, "parent", None)

                if parent is None:
                    break

                text = clean_text(
                    parent.get_text(" ", strip=True)
                )

                date_match = re.search(
                    r"\b\d{1,2}\.\s*"
                    r"(?:januar|februar|marts|april|maj|juni|"
                    r"juli|august|september|oktober|november|december)"
                    r"\s+\d{4}\b",
                    text,
                    re.IGNORECASE,
                )

                if date_match:
                    published_date = parse_date(
                        date_match.group()
                        .replace(". ", " ")
                    )
                    break

        # Only save dated items from the news listing.
        # This removes menus and ordinary site links.
        if not published_date:
            continue

        article = create_article(
            source,
            title,
            url,
            published_date,
        )

        if valid_article(article):
            articles.append(article)
            seen_urls.add(url)

    print(
        f"{source}: {len(articles)} articles found"
    )

    return articles


# ============================================================
# 3. FSR - DANSKE REVISORER
# ============================================================

def collect_fsr():

    source = "FSR - danske revisorer"

    base_url = "https://www.fsr.dk"

    pages = [
        (
            "https://www.fsr.dk/"
            "vaerktoejer/publikationer/"
            "faglig-opdatering"
        ),
        (
            "https://www.fsr.dk/"
            "politik-analyse/"
            "nyheder-og-pressemeddelelser"
        ),
    ]

    print(f"\nCollecting: {source}")

    articles = []

    for page_url in pages:

        try:
            soup = fetch_page(page_url)

        except Exception as error:
            print(
                f"FSR page failed: "
                f"{page_url} -> {error}"
            )
            continue

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = link.get("href", "")

            title = clean_text(
                link.get_text(
                    " ",
                    strip=True,
                )
            )

            if not title:
                continue

            url = normalize_url(
                base_url,
                href,
            )

            parsed = urlparse(url)

            if parsed.netloc not in [
                "fsr.dk",
                "www.fsr.dk",
            ]:
                continue

            published_date = (
                find_date_near_element(link)
            )

            # A dated article is much less likely
            # to be a navigation link.
            if not published_date:
                continue

            article = create_article(
                source,
                title,
                url,
                published_date,
            )

            if valid_article(article):
                articles.append(article)

    print(
        f"{source}: {len(articles)} articles found"
    )

    return articles


# ============================================================
# 4. EUROPEAN COMMISSION - TAXATION & CUSTOMS
# ============================================================

def collect_eu_tax():

    source = (
        "European Commission - "
        "Taxation and Customs Union"
    )

    base_url = (
        "https://taxation-customs.ec.europa.eu"
    )

    news_url = (
        "https://taxation-customs.ec.europa.eu/"
        "index_en"
    )

    print(f"\nCollecting: {source}")

    soup = fetch_page(news_url)

    articles = []

    for link in soup.find_all("a", href=True):

        href = link.get("href", "")

        title = clean_text(
            link.get_text(" ", strip=True)
        )

        if not title:
            continue

        url = normalize_url(
            base_url,
            href,
        )

        parsed = urlparse(url)

        if (
            "taxation-customs.ec.europa.eu"
            not in parsed.netloc
        ):
            continue

        # TAXUD news article URLs contain /news/
        if "/news/" not in parsed.path:
            continue

        published_date = find_date_near_element(
            link
        )

        article = create_article(
            source,
            title,
            url,
            published_date,
        )

        if valid_article(article):
            articles.append(article)

    print(
        f"{source}: {len(articles)} articles found"
    )

    return articles


# ============================================================
# 5. EFRAG
# ============================================================

def collect_efrag():

    source = "EFRAG"

    base_url = "https://www.efrag.org"

    news_url = (
        "https://www.efrag.org/"
        "en/news-and-calendar/news"
    )

    print(f"\nCollecting: {source}")

    soup = fetch_page(news_url)

    articles = []

    for link in soup.find_all("a", href=True):

        href = link.get("href", "")

        title = clean_text(
            link.get_text(" ", strip=True)
        )

        if not title:
            continue

        url = normalize_url(
            base_url,
            href,
        )

        parsed = urlparse(url)

        if "efrag.org" not in parsed.netloc:
            continue

        # Individual EFRAG news articles
        if (
            "/en/news-and-calendar/news/"
            not in parsed.path
        ):
            continue

        published_date = find_date_near_element(
            link
        )

        article = create_article(
            source,
            title,
            url,
            published_date,
        )

        if valid_article(article):
            articles.append(article)

    print(
        f"{source}: {len(articles)} articles found"
    )

    return articles


# ============================================================
# RUN ALL COLLECTORS
# ============================================================

def collect_all():

    collectors = [
        collect_digst,
        collect_erhvervsstyrelsen,
        collect_fsr,
        collect_eu_tax,
        collect_efrag,
    ]

    all_articles = []

    for collector in collectors:

        try:
            articles = collector()

            all_articles.extend(
                articles
            )

        except Exception as error:

            # One broken source should NOT stop
            # the other sources.
            print(
                f"\nWARNING: "
                f"{collector.__name__} failed."
            )

            print(
                f"Reason: {error}"
            )

    return all_articles


# ============================================================
# SAVE DATA
# ============================================================

def save_articles(articles):

    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    new_df = pd.DataFrame(
        articles,
        columns=COLUMNS,
    )

    print(
        f"\nCollected "
        f"{len(new_df)} records "
        f"in this run."
    )

    # Load historical data
    if os.path.exists(OUTPUT_FILE):

        try:
            old_df = pd.read_csv(
                OUTPUT_FILE
            )

        except Exception as error:

            print(
                "Could not read old CSV:"
            )

            print(error)

            old_df = pd.DataFrame(
                columns=COLUMNS
            )

    else:

        old_df = pd.DataFrame(
            columns=COLUMNS
        )

    # Ensure columns exist
    for column in COLUMNS:

        if column not in old_df.columns:
            old_df[column] = ""

    old_df = old_df[COLUMNS]

    combined = pd.concat(
        [
            old_df,
            new_df,
        ],
        ignore_index=True,
    )

    # Remove completely empty URLs
    combined = combined[
        combined["url"]
        .fillna("")
        .str.strip()
        .ne("")
    ]

    # URL is our primary identifier
    combined = combined.drop_duplicates(
        subset=["url"],
        keep="last",
    )

    # Sort newest first where possible
    combined = combined.sort_values(
        by=[
            "published_date",
            "source",
        ],
        ascending=[
            False,
            True,
        ],
        na_position="last",
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"Saved {len(combined)} "
        f"unique articles to "
        f"{OUTPUT_FILE}"
    )

    if not combined.empty:

        print("\nArticles by source:")

        counts = (
            combined["source"]
            .value_counts()
        )

        for source, count in counts.items():

            print(
                f"  {source}: {count}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "=================================="
    )

    print(
        "Communication Monitor Collector v2"
    )

    print(
        "=================================="
    )

    articles = collect_all()

    save_articles(articles)

    print(
        "\nCollection finished."
    )
