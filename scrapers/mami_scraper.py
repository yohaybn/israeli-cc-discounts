"""Scraper for Mami - מאמי (https://www.hi-mami.com/), a coupon and benefits club.

Two public, server-rendered sources, no login:
* ``/brands`` - brand tiles (``h3`` = name, ``p`` = English name and the standing benefit,
  e.g. "10% צבירת Mami Money").
* ``/categories/<slug>`` - current campaign tiles (``a[href*=campaignId]``, ``h3`` = the deal,
  first ``p`` = the brand). Campaigns are time-limited.
"""

import re
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, percent_value

SOURCE_KEY = "mami"
CLUB_NAME = "Mami - מאמי"
BASE_URL = "https://www.hi-mami.com/"
BRANDS_URL = "https://www.hi-mami.com/brands"
LIMITATIONS = "לחברי מועדון Mami (אפליקציה/אתר); רוב ההטבות ברכישה אונליין, מבצעים מוגבלים בזמן"
CATEGORY_RE = re.compile(r'href="(/categories/[a-z0-9-]+)"')


def _record(name: str, text: str, href: str, category: str = "") -> dict[str, Any]:
    record = {
        "club": CLUB_NAME,
        "business_name": name,
        "discount": text or name,
        "discount_url": urljoin(BASE_URL, href),
        "discount_type": "billing_discount",
        "discount_value": percent_value(text),
        "has_physical_store": False,
        "branches": [],
        "limitations": LIMITATIONS,
    }
    if category:
        record["category"] = category
    return record


def parse_brands(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select('a[href^="/brands/"]'):
        name_node = tile.select_one("h3")
        if "/brands/c/" in tile["href"] or not name_node:
            continue
        paras = [clean(p.get_text(" ", strip=True)) for p in tile.select("p")]
        benefit = paras[-1] if len(paras) > 1 else (paras[0] if paras and re.search(r"\d", paras[0]) else "")
        records.append(_record(clean(name_node.get_text(" ", strip=True)), benefit, tile["href"].split("?")[0]))
    return records


def parse_campaigns(html: str, category: str = "") -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select('a[href*="campaignId"]'):
        deal = tile.select_one("h3")
        brand = tile.select_one("p")
        name = clean(brand.get_text(" ", strip=True)) if brand else ""
        text = clean(deal.get_text(" ", strip=True)) if deal else ""
        if name:
            records.append(_record(name, text, tile["href"], category))
    return records


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    home = fetch(BASE_URL)
    records = parse_brands(fetch(BRANDS_URL))
    for path in dict.fromkeys(CATEGORY_RE.findall(home)):
        try:
            records.extend(parse_campaigns(fetch(urljoin(BASE_URL, path)), path.rsplit("/", 1)[-1]))
        except Exception as exc:  # one category should not sink the run
            print(f"WARNING: Mami {path} failed: {exc}")
    return dedupe(records)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL), "brands.html": fetch(BRANDS_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
