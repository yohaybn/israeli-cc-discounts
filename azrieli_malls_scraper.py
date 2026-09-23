"""Scraper for the coupons of קניוני עזריאלי (https://www.azrielimalls.co.il/coupons).

The coupons page is server-rendered (Next.js) and public. Each coupon card (``a`` whose class
contains ``card-container``) links to ``/malls/<mall>/coupons/<id>`` and shows the store name
(``card-header-text``), the deal (``card-title`` / ``aria-label``), the participating mall
(``mall-location``) and the validity date. The same deal is repeated per mall, so cards are
grouped by store + deal and the malls are listed in ``limitations``. CSS module class names carry
a hash suffix, so selectors match on the stable part only.
"""

from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, fetch_text, saving_percent

SOURCE_KEY = "azrieli_malls"
CLUB_NAME = "קניוני עזריאלי"
BASE_URL = "https://www.azrielimalls.co.il/"
SOURCE_URL = "https://www.azrielimalls.co.il/coupons"


def _text(card, part: str) -> str:
    node = card.select_one(f'[class*="{part}"]')
    return clean(node.get_text(" ", strip=True)) if node else ""


def parse(html: str) -> list[dict[str, Any]]:
    start = (html or "").find("coupons-list")
    soup = BeautifulSoup(html[max(0, start - 200):] if start >= 0 else (html or ""), "html.parser")
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for card in soup.select('a[class*="card-container"]'):
        store = _text(card, "card-header-text")
        deal = _text(card, "card-title") or clean(card.get("aria-label"))
        if not store or not deal:
            continue
        mall = _text(card, "mall-location")
        validity = _text(card, "card-validity")
        key = (store, deal)
        record = grouped.get(key)
        if record is None:
            record = grouped[key] = {
                "club": CLUB_NAME,
                "business_name": store,
                "discount": deal,
                "discount_url": urljoin(BASE_URL, card.get("href") or ""),
                "discount_type": "voucher",
                "discount_value": saving_percent(deal),
                "has_physical_store": True,
                "branches": [],
                "_malls": [],
                "_validity": validity,
            }
        if mall and mall not in record["_malls"]:
            record["_malls"].append(mall)
    records = []
    for record in grouped.values():
        malls = record.pop("_malls")
        validity = record.pop("_validity")
        parts = ["קופון בקניוני עזריאלי"]
        if malls:
            parts.append("קניונים משתתפים: " + ", ".join(malls))
        if validity:
            parts.append(validity)
        record["limitations"] = "; ".join(parts)
        records.append(record)
    return records


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(SOURCE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"coupons.html": fetch(SOURCE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
