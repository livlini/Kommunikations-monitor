import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SOURCE_NAME = "Digitaliseringsstyrelsen"
ARCHIVE_URL = "https://digst.dk/nyheder/nyhedsarkiv/"
BASE_URL = "https://digst.dk"

HEADERS = {
    "User-Agent": "CommunicationMonitor/1.0"
}


def collect_digst_news():
    print("Fetching Digitaliseringsstyrelsen...")

    response = requests.get(
        ARCHIVE_URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    # Find links that point to individual news archive articles
    for link in soup.find_all("a", href=True):
        href = link["href"]
        title = link.get_text(" ", strip=True)

        if not title:
            continue

        # Individual DIGST news articles normally live below
        # /nyheder/nyhedsarkiv/YYYY/...
        if re.search(r"/nyheder/nyhedsarkiv/\d{4}/", href):
            url = urljoin(BASE_URL, href)

            articles.append({
                "source": SOURCE_NAME,
                "title": title,
                "url": url
            })

    df = pd.DataFrame(articles)

    if df.empty:
        print("No articles found.")
        return df

    # Remove duplicates
    df = df.drop_duplicates(subset=["url"])

    print(f"Found {len(df)} articles.")

    return df


def save_articles(new_articles):
    os.makedirs("data", exist_ok=True)

    filepath = "data/articles.csv"

    # If we already have old articles, keep them
    if os.path.exists(filepath):
        old_articles = pd.read_csv(filepath)

        combined = pd.concat(
            [old_articles, new_articles],
            ignore_index=True
        )
    else:
        combined = new_articles

    # Avoid saving the same article more than once
    combined = combined.drop_duplicates(
        subset=["url"],
        keep="last"
    )

    combined.to_csv(
        filepath,
        index=False
    )

    print(
        f"Saved {len(combined)} total articles "
        f"to {filepath}"
    )


if __name__ == "__main__":
    articles = collect_digst_news()
    save_articles(articles)
