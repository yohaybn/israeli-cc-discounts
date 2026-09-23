"""Scraper for טוב+ (https://tovplus.org.il/), the benefits club of Israel's state employees.

Built on the dolcemaster platform; see ``dolcemaster_platform`` for the crawl. Category pages are
public (no login) and embed their products with club and market prices.
"""

from typing import Any, Callable

import dolcemaster_platform as platform
from scraper_utils import dedupe, fetch_text, is_online_only

SOURCE_KEY = "tovplus"
CLUB_NAME = "טוב פלוס"
BASE_URL = "https://tovplus.org.il"
SEED_CATEGORY = 1241
LIMITATIONS = "לעובדי המדינה חברי טוב+; רכישה/מימוש דרך אתר המועדון"


def parse(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for product in products:
        name = platform.product_name(product)
        if not name:
            continue
        text, percent = platform.benefit_text(product)
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text or name,
            "discount_url": f"{BASE_URL}/product/{product.get('product_id')}",
            "discount_type": "voucher",
            "discount_value": percent,
            "has_physical_store": not is_online_only(text),
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(platform.crawl(BASE_URL, SEED_CATEGORY, fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"category.html": fetch(f"{BASE_URL}/category/{SEED_CATEGORY}")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
