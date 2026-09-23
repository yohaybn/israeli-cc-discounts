"""Scraper for מועדון W (the "דאבל יו" credit card of GOLF group and Steimatzky, by Isracard).

The public page https://w-card.co.il/ lists the card's benefits as Elementor image boxes
(title such as "10% צבירת נקודות" and a short description). No login is needed.
"""

from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "w_card"
CLUB_NAME = "מועדון W"
PAGE_URL = "https://w-card.co.il/"
LIMITATIONS = "למחזיקי כרטיס האשראי דאבל יו (ישראכרט); בכפוף לתקנון המועדון"


def business_for(text: str) -> str:
    golf, steimatzky = "GOLF" in text, "סטימצקי" in text
    if golf and steimatzky:
        return "GOLF וסטימצקי"
    if steimatzky:
        return "סטימצקי"
    if golf:
        return "קבוצת GOLF"
    if "מזון" in text:
        return "ענף המזון"
    if "ספרים" in text or "רבי מכר" in text:
        return "סטימצקי"
    return CLUB_NAME


def parse(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for box in soup.select(".elementor-image-box-content"):
        title = box.select_one(".elementor-image-box-title")
        desc = box.select_one(".elementor-image-box-description")
        text = clean(" ".join(n.get_text(" ", strip=True) for n in (title, desc) if n))
        if not text:
            continue
        records.append({
            "club": CLUB_NAME,
            "business_name": business_for(text),
            "discount": text,
            "discount_url": PAGE_URL,
            "discount_type": "discount",
            "discount_value": percent_value(text),
            "has_physical_store": True,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(PAGE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(PAGE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
