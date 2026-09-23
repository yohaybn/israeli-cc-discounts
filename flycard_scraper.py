"""Scraper for FLY CARD (El Al x Isracard) card benefits (https://www.isracard.co.il/flycard/private).

El Al's own FLY CARD pages load content from an API behind a bot challenge, so this reads the
public Isracard FLY CARD page. Its benefits are a Wix repeater: each list item has an ``<h4>``
title followed by a description paragraph.
"""

import re
from typing import Any, Callable

from scraper_utils import dedupe, fetch_text, html_to_text, percent_value

SOURCE_KEY = "flycard"
CLUB_NAME = "FLY CARD אל על"
URL = "https://www.isracard.co.il/flycard/private"
LIMITATIONS = "למחזיקי כרטיס FLY CARD של ישראכרט/אמריקן אקספרס; בכפוף לתנאי ההטבות באתרי אל על וישראכרט"
ITEM_SPLIT = re.compile(r'role="listitem"')
TITLE_RE = re.compile(r"<h4[^>]*>(.*?)</h4>", re.S)
DESC_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.S)


def parse(html: str) -> list[dict[str, Any]]:
    records = []
    for chunk in ITEM_SPLIT.split(html)[1:]:
        title_m = TITLE_RE.search(chunk)
        if not title_m:
            continue
        title = html_to_text(title_m.group(1))
        desc_m = DESC_RE.search(chunk, title_m.end())
        desc = html_to_text(desc_m.group(1)) if desc_m else ""
        if not title:
            continue
        records.append({
            "club": CLUB_NAME,
            "business_name": "אל על",
            "discount": f"{title} - {desc}" if desc else title,
            "discount_url": URL,
            "discount_type": "card_benefit",
            "discount_value": percent_value(f"{title} {desc}"),
            "has_physical_store": False,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"flycard.html": fetch(URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items:
        print(item["discount"][:120])
