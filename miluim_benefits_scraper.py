"""Scraper for the IDF reservists' benefits world (https://www.miluim.idf.il/benefits-list).

The site is a React app. It reads its public benefits list, without login, from
``https://api.miluim.idf.il/api/v1/Benefits`` - the same call the app makes.
"""

import json
from typing import Any, Callable
from urllib.parse import quote

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "miluim_benefits"
CLUB_NAME = "עולם ההטבות למילואימניקים"
SITE_URL = "https://www.miluim.idf.il"
API_URL = "https://api.miluim.idf.il/api/v1/Benefits"
LIMITATIONS = "למשרתי מילואים לפי תנאי הזכאות של כל הטבה"


def parse(payload: str | dict[str, Any]) -> list[dict[str, Any]]:
    data = json.loads(payload) if isinstance(payload, str) else payload
    records = []
    for item in (data or {}).get("benefits") or []:
        title = clean(item.get("title"))
        if not title:
            continue
        desc = clean(item.get("description"))
        tags = ", ".join(clean(f.get("text")) for f in item.get("filters") or [] if f.get("text"))
        eligible = ", ".join(clean(e.get("text")) for e in item.get("eligibleFor") or [] if e.get("text"))
        url = item.get("url") or "/benefits-list"
        records.append({
            "club": CLUB_NAME,
            "business_name": title,
            "discount": desc or title,
            "discount_url": SITE_URL + quote(url),
            "discount_type": "benefit",
            "discount_value": percent_value(desc),
            "has_physical_store": False,
            "branches": [],
            "limitations": "; ".join(x for x in [LIMITATIONS, f"קטגוריה: {tags}" if tags else "", f"זכאים: {eligible}" if eligible else ""] if x),
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(API_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"benefits.json": fetch(API_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
