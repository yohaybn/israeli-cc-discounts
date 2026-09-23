"""Scraper for שחר, the culture and leisure club of הסתדרות המהנדסים (https://www.m-shachar.org.il/benefit/).

The public benefits page lists each benefit as an ``a.stand_item`` tile with a title, an optional
sub-title and a summary line. No login.
"""

from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "shachar"
CLUB_NAME = "שחר"
SOURCE_URL = "https://www.m-shachar.org.il/benefit/"
LIMITATIONS = "לחברי מועדון שחר (מהנדסים, אדריכלים ואקדמאים במקצועות הטכנולוגיים)"


def parse(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select("a.stand_item"):
        title = tile.select_one(".stand_title")
        name = clean(title.get_text(" ", strip=True) if title else tile.get("title"))
        if not name:
            continue
        parts = [clean(n.get_text(" ", strip=True)) for n in tile.select(".stand_sub_title, .stand_summary")]
        text = " - ".join(p for p in parts if p)
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text or name,
            "discount_url": tile.get("href") or SOURCE_URL,
            "discount_type": "billing_discount",
            "discount_value": percent_value(text),
            "has_physical_store": True,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(SOURCE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"benefits.html": fetch(SOURCE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
