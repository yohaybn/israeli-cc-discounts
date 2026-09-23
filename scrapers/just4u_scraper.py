"""Scraper for Just4u / NEW CARD (https://www.just4u.co.il/), a gift-voucher club.

The site is an Angular app. Its public, unauthenticated JSON endpoint
``/api/newapi/getHomepageItems`` (the same call the app makes for the home page) lists the voucher
items by group with their face price, plus featured partner businesses.
"""

import json
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text

SOURCE_KEY = "just4u"
CLUB_NAME = "Just4u / NEW CARD"
BASE_URL = "https://www.just4u.co.il"
API_URL = f"{BASE_URL}/api/newapi/getHomepageItems"
LIMITATIONS = "שובר מתנה לרכישה דרך Just4u; מימוש אצל בתי העסק המשתתפים"


def parse(payload: str | dict[str, Any]) -> list[dict[str, Any]]:
    data = json.loads(payload) if isinstance(payload, str) else payload
    records = []
    seen: set[str] = set()
    for group in (data or {}).get("groups") or []:
        group_name = clean(group.get("name"))
        for item in group.get("items") or []:
            name = clean(item.get("name"))
            if not name:
                continue
            kind = item.get("type")
            if kind == "supplier":
                text = f"בית עסק שמכבד שוברי Just4u ({group_name})"
                url = f"{BASE_URL}/supplier/{item.get('id')}"
                dtype = "gift_card"
            else:
                price = item.get("price10") or 0
                text = f"שובר {name}" + (f" - {price:g} ₪" if price else "") + (f" ({group_name})" if group_name else "")
                url = f"{BASE_URL}/gifts/{item.get('id')}"
                dtype = "voucher"
            if url in seen:
                continue
            seen.add(url)
            records.append({
                "club": CLUB_NAME,
                "business_name": name,
                "discount": text,
                "discount_url": url,
                "discount_type": dtype,
                "discount_value": None,
                "has_physical_store": item.get("coupon_type") != "digital" or kind == "supplier",
                "branches": [],
                "limitations": LIMITATIONS,
            })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(API_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.json": fetch(API_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
