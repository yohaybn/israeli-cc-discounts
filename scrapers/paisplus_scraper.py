"""Public Pais Plus voucher and attraction catalog, via Dolcemaster category pages."""

from typing import Any, Callable

import dolcemaster_platform as platform
from scraper_utils import clean, dedupe, fetch_text, is_online_only

SOURCE_KEY = "paisplus"
CLUB_NAME = "פיס פלוס"
BASE_URL = "https://paisplus.co.il"
SEED_CATEGORY = 302
LIMITATIONS = "למנויי פיס פלוס; מימוש ורכישה בכפוף לתנאי המועדון"
PUBLIC_VOUCHER_TYPES = {1, 3, 4, 6}  # code, attraction/event, managed-value voucher; exclude physical goods (2)


def parse(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in products:
        kind = item.get("product_type_id")
        if kind not in PUBLIC_VOUCHER_TYPES or item.get("out_of_stock") == "Y":
            continue
        name, ident = platform.product_name(item), clean(item.get("product_id"))
        price = platform._price(item.get("club_price"))
        market = platform._price(item.get("market_price"))
        if not name or not ident or not price or not market or price >= market:
            continue
        text, percent = platform.benefit_text(item)
        records.append({
            "club": CLUB_NAME, "business_name": name, "discount": text,
            "discount_url": f"{BASE_URL}/product/{ident}", "discount_type": "coupon",
            "discount_value": None, "price": price, "original_price": market,
            "voucher_type": clean(item.get("product_type_name")) or "קופון",
            "has_physical_store": not is_online_only(name, text), "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(platform.crawl_public_catalog(BASE_URL, SEED_CATEGORY, fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"category.html": fetch(f"{BASE_URL}/category/{SEED_CATEGORY}")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} coupons")
