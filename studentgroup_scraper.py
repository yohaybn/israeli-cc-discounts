"""Scraper for סטודנט גרופ (https://studentgroup.co.il/), a student coupon club.

Each coupon is a WooCommerce ``product`` exposed through the public WordPress REST API
(``/wp-json/wp/v2/product``). The benefit text is in the SEO title
(``yoast_head_json.title``, e.g. "קופון ZER4U ... מעניק 15% הנחה כולל כפל מבצעים | מעודכן 2026").
No login is needed to read it.
"""

import re
from html import unescape
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, percent_value
from wp_catalog import fetch_wp_collection

SOURCE_KEY = "studentgroup"
CLUB_NAME = "סטודנט גרופ"
BASE_URL = "https://studentgroup.co.il/"
FIELDS = "id,link,title,yoast_head_json.title"
LIMITATIONS = "לחברי סטודנט גרופ; קוד קופון לרכישה אונליין"
SUFFIX_RE = re.compile(r"\s*\|\s*(?:מעודכן\s*\d{4}|סטודנט גרופ).*$")


def parse(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in items:
        name = clean(unescape((item.get("title") or {}).get("rendered") or ""))
        if not name:
            continue
        seo = clean(unescape(((item.get("yoast_head_json") or {}).get("title")) or ""))
        text = SUFFIX_RE.sub("", seo) or name
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text,
            "discount_url": item.get("link") or BASE_URL,
            "discount_type": "voucher",
            "discount_value": percent_value(text),
            "has_physical_store": False,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch_wp_collection(BASE_URL, "product", FIELDS, fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"products_page1.json": fetch(f"{BASE_URL}wp-json/wp/v2/product?per_page=100&page=1&_fields={FIELDS}")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
