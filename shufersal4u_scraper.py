"""Scraper for the Shufersal 4U credit-card club (שופרסל 4U).

The club site https://www.shufersal4u.co.il/ shows its benefit catalog publicly (no login is
needed to browse; login is only needed to buy). The home page links category pages
(?page=category&id=N). Each category page shows benefit tiles with a title and a
"לרכישה ב-X ₪ / בשווי Y ₪" price line. This module walks the categories (and any
sub-category links they show) and keeps one record per benefit uuid.
"""

import re
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "shufersal4u"
CLUB_NAME = "שופרסל 4U"
BASE_URL = "https://www.shufersal4u.co.il/"
CATEGORY_RE = re.compile(r"page=category&id=(\d+)")
UUID_RE = re.compile(r"uuid=([0-9A-Fa-f-]+)")
PRICE_RE = re.compile(r"לרכישה ב-?\s*₪?\s*([\d,.]+)\s*₪?.*?(?:בשווי|במקום)\s*₪?\s*([\d,.]+)", re.S)


def category_links(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    found: dict[str, str] = {}
    for link in soup.select('a[href*="page=category"]'):
        match = CATEGORY_RE.search(link.get("href") or "")
        name = clean(link.get_text(" ", strip=True))
        if match and (match.group(1) not in found or found[match.group(1)] == "צפיה בהטבות נוספות"):
            found[match.group(1)] = name
    return found


def saving_percent(description: str) -> float | None:
    match = PRICE_RE.search(description or "")
    if not match:
        return percent_value(description)
    try:
        price, worth = (float(v.replace(",", "")) for v in match.groups())
    except ValueError:
        return None
    if worth <= 0 or price >= worth:
        return None
    return round((worth - price) / worth * 100, 1)


def parse_category(html: str, category: str = "") -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select('a.box-item[href*="page=Benefit"]'):
        title = clean(tile.select_one("h4").get_text(" ", strip=True)) if tile.select_one("h4") else ""
        if not title:
            continue
        desc_node = tile.select_one("p.description")
        description = clean(desc_node.get_text(" ", strip=True)) if desc_node else ""
        href = urljoin(BASE_URL, tile.get("href"))
        match = UUID_RE.search(href)
        url = urljoin(BASE_URL, f"?page=Benefit&uuid={match.group(1)}") if match else href
        record = {
            "club": CLUB_NAME,
            "business_name": title,
            "discount": description or title,
            "discount_url": url,
            "discount_type": "voucher",
            "discount_value": saving_percent(description),
            "has_physical_store": True,
            "branches": [],
            "limitations": "רכישה דרך אתר המועדון למחזיקי כרטיס שופרסל",
        }
        if category and category != "צפיה בהטבות נוספות":
            record["category"] = category
        records.append(record)
    return records


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    home = fetch(BASE_URL)
    queue = category_links(home)
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    while queue:
        cat_id, name = queue.popitem()
        if cat_id in seen:
            continue
        seen.add(cat_id)
        try:
            html = fetch(urljoin(BASE_URL, f"?page=category&id={cat_id}"))
        except Exception as exc:
            print(f"WARNING: category {cat_id} failed: {exc}")
            continue
        records.extend(parse_category(html, name))
        for sub_id, sub_name in category_links(html).items():
            if sub_id not in seen and sub_id not in queue:
                queue[sub_id] = sub_name
    by_url: dict[str, dict[str, Any]] = {}
    for record in records:
        existing = by_url.get(record["discount_url"])
        if existing is None or ("category" not in existing and "category" in record):
            by_url[record["discount_url"]] = record
    return dedupe(list(by_url.values()))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
