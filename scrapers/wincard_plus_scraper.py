"""Scraper for WinCard+ (https://m-shuk.net/wincard/), the מחסני השוק credit card with max.

The public card page lists the card's own benefits as Elementor icon boxes (title + description).
"""

import re
from typing import Any, Callable

from scraper_utils import dedupe, fetch_text, html_to_text, percent_value

SOURCE_KEY = "wincard_plus"
CLUB_NAME = "WinCard+ מחסני השוק"
URL = "https://m-shuk.net/wincard/"
LIMITATIONS = "למחזיקי כרטיס האשראי WinCard+ (מחסני השוק בשיתוף max)"
BOX_RE = re.compile(
    r'<h3 class="elementor-icon-box-title">(.*?)</h3>\s*<p class="elementor-icon-box-description">(.*?)</p>',
    re.S,
)


def parse(html: str) -> list[dict[str, Any]]:
    records = []
    for title_html, desc_html in BOX_RE.findall(html):
        title, desc = html_to_text(title_html), html_to_text(desc_html)
        if not title:
            continue
        records.append({
            "club": CLUB_NAME,
            "business_name": "מחסני השוק",
            "discount": f"{title} - {desc}" if desc else title,
            "discount_url": URL,
            "discount_type": "card_benefit",
            "discount_value": percent_value(title),
            "has_physical_store": True,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"wincard.html": fetch(URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
