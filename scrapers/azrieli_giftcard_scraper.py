"""Scraper for stores that accept the Azrieli malls gift card (עזריאלי גיפטקארד).

The card is sold and managed through BUYME, and its participating-store list is BUYME brand
398383 (linked from https://www.azrielimalls.co.il/giftcard as "בתי עסק מכבדים"). This module
reuses the BUYME fetch/parse code and relabels the records as their own club.
"""

import json
from typing import Any, Callable

from buyme_scraper import scrape_supplier, stores_to_discounts
from scraper_utils import dedupe, html_to_text

SOURCE_KEY = "azrieli_giftcard"
CLUB_NAME = "עזריאלי גיפטקארד"
BUYME_BRAND_ID = 398383
PAGE_URL = "https://www.azrielimalls.co.il/giftcard"
DISCOUNT_TEXT = "מכבד את עזריאלי גיפטקארד (בסניפים בקניוני עזריאלי)"


def normalize_azrieli(stores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    by_title = {s.get("title"): s for s in stores if isinstance(s, dict)}
    for item in stores_to_discounts(stores, supplier_ids_fallback=[BUYME_BRAND_ID]):
        store = by_title.get(item.get("business_name")) or {}
        regions = [r for r in store.get("supplier_regions") or [] if r]
        online = regions == ["מימוש אונליין"]
        small_print = html_to_text(store.get("smallPrint") or "")
        limitations = " | ".join(part for part in (small_print, f"אזורים: {', '.join(regions)}" if regions else "") if part)
        records.append({
            "club": CLUB_NAME,
            "business_name": item["business_name"],
            "discount": DISCOUNT_TEXT,
            "discount_url": item.get("discount_url") or PAGE_URL,
            "discount_type": "gift_card",
            "discount_value": None,
            "has_physical_store": not online,
            "branches": [],
            "limitations": limitations,
        })
    return dedupe(records)


def fetch_raw(fetch: Callable[[int], dict] = scrape_supplier) -> dict[str, str]:
    return {"buyme_brand_398383.json": json.dumps(fetch(BUYME_BRAND_ID), ensure_ascii=False)}


def scrape(fetch: Callable[[int], dict] = scrape_supplier) -> list[dict[str, Any]]:
    return normalize_azrieli(fetch(BUYME_BRAND_ID).get("stores") or [])


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} stores")
    for item in items[:3]:
        print(item)
