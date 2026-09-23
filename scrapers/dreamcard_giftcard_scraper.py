"""Scraper for the chains that accept the DREAM CARD gift card (FOX group).

The public page https://www.dcgift.co.il/brands lists each accepting brand as a logo (``img alt``)
next to a short description and a store-list link. No login is needed.
"""

from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text

SOURCE_KEY = "dreamcard_giftcard"
CLUB_NAME = "DREAMCARD gift card / דרים קארד גיפט"
PAGE_URL = "https://www.dcgift.co.il/brands"
DISCOUNT_TEXT = "מכבד את כרטיס המתנה DREAM CARD"
LIMITATIONS = "ללא כפל עם הטבות מועדון; לא בחנויות עודפים (לפי תקנון dcgift.co.il/include)"


def parse(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for img in soup.select("div.w_20 > img[alt]"):
        name = clean(img.get("alt"))
        row = img.parent.parent if img.parent else None
        if not name or row is None:
            continue
        link = row.select_one("a[href]")
        text = row.select_one("p")
        about = clean(text.get_text(" ", strip=True).replace("לרשימת חנויות >", "")) if text else ""
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": DISCOUNT_TEXT,
            "discount_url": link["href"] if link else PAGE_URL,
            "discount_type": "gift_card",
            "discount_value": None,
            "has_physical_store": True,
            "branches": [],
            "limitations": " | ".join(p for p in (LIMITATIONS, about) if p),
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(PAGE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"brands.html": fetch(PAGE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} brands")
    for item in items[:3]:
        print(item)
