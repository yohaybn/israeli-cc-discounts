"""Scraper for the benefits of חתול פיננסי (https://moneyplan.co.il/benefits/).

The benefits are a custom ``benefits`` post type exposed through the public WordPress REST API
(``/wp-json/wp/v2/benefits``). The benefit text is the SEO description
(``yoast_head_json.og_description``). No login is needed to read it.
"""

from html import unescape
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, percent_value
from wp_catalog import fetch_wp_collection

SOURCE_KEY = "moneyplan"
CLUB_NAME = "חתול פיננסי"
BASE_URL = "https://moneyplan.co.il/"
FIELDS = "id,link,title,yoast_head_json.og_description"
LIMITATIONS = "לחברי קהילת חתול פיננסי; מימוש דרך קישור ההטבה באתר"


def parse(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in items:
        name = clean(unescape((item.get("title") or {}).get("rendered") or ""))
        if not name:
            continue
        text = clean(unescape(((item.get("yoast_head_json") or {}).get("og_description")) or "")) or name
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text,
            "discount_url": item.get("link") or BASE_URL + "benefits/",
            "discount_type": "voucher",
            "discount_value": percent_value(text),
            "has_physical_store": False,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch_wp_collection(BASE_URL, "benefits", FIELDS, fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"benefits.json": fetch(f"{BASE_URL}wp-json/wp/v2/benefits?per_page=100&page=1&_fields={FIELDS}")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
