"""Scraper for the networks and businesses that accept Raayonit's "Global Tav" (גלובל תו) gift voucher."""

from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text

SOURCE_KEY = "raayonit_global"
CLUB_NAME = "גלובל קארד - רעיונית"
SOURCE_URL = "https://www.raayonit.co.il/club/?ClubNum=18&ClubVoucherTypeNum=47"
DISCOUNT_TEXT = "מכבד את שובר גלובל תו של רעיונית"


def _record(name: str, url: str, limitations: str, category: str = "") -> dict[str, Any]:
    record = {
        "club": CLUB_NAME,
        "business_name": name,
        "discount": DISCOUNT_TEXT,
        "discount_url": url,
        "discount_type": "gift_card",
        "discount_value": None,
        "has_physical_store": True,
        "branches": [],
        "limitations": limitations,
    }
    if category:
        record["category"] = category
    return record


def parse_raayonit_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    # Chains: one logo tile per network.
    for anchor in soup.select("a[href*='NetworkNum=']"):
        title = anchor.select_one(".title")
        name = clean(title.get_text(" ", strip=True) if title else anchor.get_text(" ", strip=True))
        if name:
            records.append(_record(name, anchor["href"].strip(), "רשת - מימוש בסניפי הרשת", "רשתות"))

    # Individual businesses listed in the supplier grid; branches of one business are merged.
    suppliers: dict[str, dict[str, Any]] = {}
    for row in soup.select("div.row[rtype=summary]"):
        title = row.select_one(".title > b")
        name = clean(title.get_text(" ", strip=True) if title else "")
        if not name:
            continue
        address = clean((row.select_one(".address") or row).get_text(" ", strip=True)) if row.select_one(".address") else ""
        phone = clean(row.select_one(".phones").get_text(" ", strip=True)) if row.select_one(".phones") else ""
        website = row.select_one("a.grid_website[href]")
        parts = []
        if address:
            parts.append(f"כתובת: {address}")
        if phone:
            parts.append(f"טלפון: {phone}")
        if website:
            parts.append(f"אתר: {website['href'].strip()}")
        limitation = " | ".join(parts)
        existing = suppliers.get(name)
        if existing:
            if limitation and limitation not in existing["limitations"]:
                existing["limitations"] = f"{existing['limitations']} || {limitation}"
            continue
        record = _record(name, SOURCE_URL, limitation, "בתי עסק")
        record["has_physical_store"] = address != "חנות אינטרנטית"
        suppliers[name] = record
        records.append(record)

    return dedupe(records)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"global_tav.html": fetch(SOURCE_URL)}


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse_raayonit_html(fetch(SOURCE_URL))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} businesses")
    for item in items[:3] + items[-3:]:
        print(item)
