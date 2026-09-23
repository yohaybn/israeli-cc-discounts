"""Scraper for Cashdo (https://cashdo.co.il/all-stores), a cashback club for online stores.

The all-stores page loads its list from the public ``/paging.json`` endpoint, which returns the
store tiles as HTML inside JSON (``content.data``). Each ``li.product`` tile has the store name,
its ``/store/...`` link and a cashback line ("עד 20% קאשבק"). No login is needed to browse.
Cashback is paid after the purchase, so records use ``billing_discount`` and are online-only.
"""

import json
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "cashdo"
CLUB_NAME = "Cashdo"
BASE_URL = "https://cashdo.co.il/"
PAGING_URL = "https://cashdo.co.il/paging.json?pt=5&ps=1000&categoryOid=&p=1"
LIMITATIONS = "קאשבק לחברי Cashdo ברכישה אונליין דרך קישור האתר/התוסף; הזיכוי מתקבל אחרי אישור הרכישה"


def parse(payload: str) -> list[dict[str, Any]]:
    data = json.loads(payload or "{}")
    html = ((data.get("content") or {}).get("data")) or ""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for tile in soup.select("li.product"):
        link = tile.select_one(".product-name a") or tile.select_one('a[href^="/store/"]')
        name = clean(link.get_text(" ", strip=True)) if link else ""
        if not name:
            continue
        promo = tile.select_one(".promo")
        text = clean(promo.get_text(" ", strip=True)) if promo else ""
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text or "קאשבק",
            "discount_url": urljoin(BASE_URL, link.get("href")),
            "discount_type": "billing_discount",
            "discount_value": percent_value(text),
            "has_physical_store": False,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(PAGING_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"paging.json": fetch(PAGING_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
