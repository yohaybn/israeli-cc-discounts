"""Scraper for מועדון יותר, the soldiers' benefits club of האגודה למען החייל (https://yoter.co.il/).

The public business list page (רשימת בתי עסק) shows every partner as an ``a.logo-item`` tile with
the business name, a short benefit line, a discount badge and category classes. No login.
"""

import re
from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, is_online_only, percent_value

SOURCE_KEY = "yoter"
CLUB_NAME = "יותר"
SOURCE_URL = "https://yoter.co.il/%D7%A8%D7%A9%D7%99%D7%9E%D7%AA-%D7%91%D7%AA%D7%99-%D7%A2%D7%A1%D7%A7/"
LIMITATIONS = "לחיילים בשירות חובה בהצגת תעודת חוגר / חברי מועדון יותר"
CAT_RE = re.compile(r"logo_cat_(\d+)")


def parse(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    categories = {}
    for link in soup.select("ul.filter-nav a[data-filter]"):
        match = CAT_RE.search(link.get("data-filter") or "")
        if match:
            categories[match.group(1)] = clean(link.get_text(" ", strip=True))
    records = []
    for tile in soup.select("a.logo-item"):
        title_node = tile.select_one(".logo-title")
        name = clean(title_node.get_text(" ", strip=True) if title_node else tile.get("title"))
        if not name:
            continue
        intro = tile.select_one(".logo-intro")
        badge = tile.select_one(".discount")
        text = clean(intro.get_text(" ", strip=True)) if intro else ""
        badge_text = clean(badge.get_text(" ", strip=True)) if badge else ""
        record = {
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text or badge_text or name,
            "discount_url": tile.get("href") or SOURCE_URL,
            "discount_type": "billing_discount",
            "discount_value": percent_value(badge_text) or percent_value(text),
            "has_physical_store": not is_online_only(text),
            "branches": [],
            "limitations": LIMITATIONS,
        }
        cats = [categories[c] for c in CAT_RE.findall(" ".join(tile.get("class") or [])) if c in categories]
        if cats:
            record["category"] = cats[0]
        records.append(record)
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(SOURCE_URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"business_list.html": fetch(SOURCE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
