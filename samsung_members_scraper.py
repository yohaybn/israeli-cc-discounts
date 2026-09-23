"""Scraper for the Samsung Members / Galaxy VIP benefits page (Samsung Israel).

The public page https://www.samsung.com/il/mobile/samsung-members/benefits/ lists the current
benefits as feature-column carousel cards (title, price/discount text, redemption link). No login
is needed to read the list; redeeming a benefit needs the Samsung Members app.
"""

from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "samsung_members"
CLUB_NAME = "Samsung Members"
PAGE_URL = "https://www.samsung.com/il/mobile/samsung-members/benefits/"
LIMITATIONS = "ללקוחות סמסונג עם אפליקציית Samsung Members; בכפוף לתנאי כל הטבה"


def parse(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for card in soup.select(".feature-column-carousel__item"):
        title = card.select_one(".feature-column-carousel__title-text")
        name = clean(title.get_text(" ", strip=True)) if title else ""
        if not name:
            continue
        body = card.select_one(".feature-column-carousel__text-text")
        text = clean(body.get_text(" ", strip=True)) if body else ""
        link = card.select_one(".feature-column-carousel__button a[href]")
        url = link["href"] if link else PAGE_URL
        if url.startswith("//"):
            url = "https:" + url
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text or name,
            "discount_url": url,
            "discount_type": "voucher",
            "discount_value": percent_value(text),
            "has_physical_store": False,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(PAGE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"benefits.html": fetch(PAGE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
