"""Scraper for the brands that accept the מחסני השוק WINcard gift card.

The brand list is a public WordPress post type (``giftcardbrands``) on https://m-shuk.net/
(shown at https://m-shuk.net/giftcardbrands/). No login is needed.
"""

from html import unescape
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text
from wp_catalog import fetch_wp_collection

SOURCE_KEY = "wincard_giftcard"
CLUB_NAME = "מחסני השוק גיפטקארד Wincard"
BASE_URL = "https://m-shuk.net/"
FIELDS = "id,link,title,yoast_head_json.og_description"
DISCOUNT_TEXT = "מכבד את כרטיס המתנה WINcard של מחסני השוק"
LIMITATIONS = "מימוש בכרטיס המתנה WINcard; רשימת המותגים עשויה להשתנות"


def parse(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in items:
        name = clean(unescape((item.get("title") or {}).get("rendered") or ""))
        if not name:
            continue
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": DISCOUNT_TEXT,
            "discount_url": item.get("link") or BASE_URL + "giftcardbrands/",
            "discount_type": "gift_card",
            "discount_value": None,
            "has_physical_store": True,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch_wp_collection(BASE_URL, "giftcardbrands", FIELDS, fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"giftcardbrands.json": fetch(f"{BASE_URL}wp-json/wp/v2/giftcardbrands?per_page=100&page=1&_fields={FIELDS}")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} brands")
    for item in items[:3]:
        print(item)
