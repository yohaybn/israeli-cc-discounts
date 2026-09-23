"""Scraper for קופונופש (https://cpnclub.co.il/).

The site's own back end exposes the club (leisure) supplier list without login at
``https://be.cpnclub.co.il/api/v2/search/club`` (paged, ``perPage`` up to 100). Each supplier is
one benefit; ``info.discount`` holds the headline percent when the club publishes one.
"""

import json
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text

SOURCE_KEY = "cpnclub"
CLUB_NAME = "קופונופש"
API_URL = "https://be.cpnclub.co.il/api/v2/search/club"
SITE_URL = "https://cpnclub.co.il/"
PER_PAGE = 100
MAX_PAGES = 30
LIMITATIONS = "רכישת שובר/כרטיס מוזל באתר קופונופש; בכפוף לתנאי הספק"


def parse(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in items:
        name = clean(item.get("name"))
        if not name:
            continue
        info = item.get("info") or {}
        percent = info.get("discount") or 0
        try:
            percent = float(percent)
        except (TypeError, ValueError):
            percent = 0.0
        text = f"עד {percent:g}% הנחה לחברי קופונופש" if percent > 0 else "כרטיסים ושוברים במחיר מוזל לחברי קופונופש"
        city = clean(info.get("city"))
        branches = [city] if city and city != "כל הארץ" else []
        slug = item.get("identOrSlug") or item.get("reference")
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text,
            "discount_url": f"{SITE_URL}supplier/{slug}" if slug else SITE_URL,
            "discount_type": "voucher",
            "discount_value": percent or None,
            "has_physical_store": bool(branches),
            "branches": branches,
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def fetch_pages(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while page <= MAX_PAGES:
        data = json.loads(fetch(f"{API_URL}?perPage={PER_PAGE}&page={page}"))
        batch = data.get("data") or []
        items.extend(batch)
        pages = (data.get("meta") or {}).get("pages") or 1
        if not batch or page >= pages:
            break
        page += 1
    return items


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch_pages(fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"search_club.json": fetch(f"{API_URL}?perPage={PER_PAGE}&page=1")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
