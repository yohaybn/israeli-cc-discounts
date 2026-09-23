"""Scraper for the brands that accept the LOVE CARD gift card (Castro-Hoodies group).

The card's public terms page (https://www.hoodies.co.il/tqnvn-love-card) names the group brands
where the card is accepted, in the clause "(קרי, המותגים: ...)". Castro, the issuer, is added
as well. No login is needed.
"""

import re
from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text

SOURCE_KEY = "love_card"
CLUB_NAME = "LOVE gift card"
PAGE_URL = "https://www.hoodies.co.il/tqnvn-love-card"
ISSUER = "קסטרו"
BRANDS_RE = re.compile(r"המותגים:\s*([^()]+?)\s*[(.;]")
DISCOUNT_TEXT = "מכבד את כרטיס המתנה LOVE CARD של קבוצת קסטרו-הודיס"
LIMITATIONS = "בחנויות הפיזיות ובאתר קסטרו; לפי תקנון LOVE CARD"


def brand_names(html: str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = clean(soup.get_text(" "))
    match = BRANDS_RE.search(text)
    if not match:
        return []
    names = [clean(n) for n in re.split(r",|\sו(?=[א-ת])", match.group(1))]
    names = [n for n in names if n and n != ISSUER and len(n) <= 30 and not n.startswith("כל ")]
    return [ISSUER] + names


def parse(html: str) -> list[dict[str, Any]]:
    return dedupe([{
        "club": CLUB_NAME,
        "business_name": name,
        "discount": DISCOUNT_TEXT,
        "discount_url": PAGE_URL,
        "discount_type": "gift_card",
        "discount_value": None,
        "has_physical_store": True,
        "branches": [],
        "limitations": LIMITATIONS,
    } for name in brand_names(html)])


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(PAGE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"terms.html": fetch(PAGE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} brands")
    for item in items[:3]:
        print(item)
