"""Scraper for the store list of the Gold Card (גולד קארד) gift card, read from the public WordPress API."""

import json
from typing import Any, Callable

from scraper_utils import dedupe, fetch_text
from wp_catalog import fetch_wp_collection, rendered, term_names

SOURCE_KEY = "goldcard"
CLUB_NAME = "גולד קארד"
BASE_URL = "https://goldcard-gift.com"
BRAND_FIELDS = "id,title,link,brand-categories,cities-category"
SKIP_CATEGORIES = {"רשת חדשה"}


def normalize_goldcard(brands, categories: dict[int, str], cities: dict[int, str]) -> list[dict[str, Any]]:
    records = []
    for brand in brands:
        name = rendered(brand, "title")
        if not name:
            continue
        cats = [categories.get(cid, "") for cid in brand.get("brand-categories") or []]
        cats = [c for c in cats if c and c not in SKIP_CATEGORIES]
        city_names = [cities.get(cid, "") for cid in brand.get("cities-category") or []]
        city_names = [c for c in city_names if c]
        record = {
            "club": CLUB_NAME,
            "business_name": name,
            "discount": "מכבד את כרטיס המתנה גולד קארד",
            "discount_url": brand.get("link") or BASE_URL,
            "discount_type": "gift_card",
            "discount_value": None,
            "has_physical_store": True,
            "branches": [],
            "limitations": f"ערים: {', '.join(city_names)}" if city_names else "",
        }
        if cats:
            record["category"] = cats[0]
        records.append(record)
    return dedupe(records)


def _collections(fetch):
    brands = fetch_wp_collection(BASE_URL, "brands", BRAND_FIELDS, fetch)
    categories = fetch_wp_collection(BASE_URL, "brand-categories", "id,name", fetch)
    cities = fetch_wp_collection(BASE_URL, "cities-category", "id,name", fetch)
    return brands, categories, cities


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    brands, categories, cities = _collections(fetch)
    return {
        "brands.json": json.dumps(brands, ensure_ascii=False),
        "brand_categories.json": json.dumps(categories, ensure_ascii=False),
        "cities.json": json.dumps(cities, ensure_ascii=False),
    }


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    brands, categories, cities = _collections(fetch)
    return normalize_goldcard(brands, term_names(categories), term_names(cities))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} stores")
    for item in items[:3]:
        print(item)
