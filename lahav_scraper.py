"""Scraper for the להב - לשכת העצמאים benefits club (https://lahav.style.co.il/).

The site runs on the shared "style" benefits platform, so the crawl is done by
style_platform.crawl: public category pages, no login (login is only needed to buy).
"""

from typing import Any, Callable

import style_platform
from scraper_utils import fetch_text

SOURCE_KEY = "lahav"
CLUB_NAME = "להב - לשכת העצמאים"
BASE_URL = "https://lahav.style.co.il/"
LIMITATIONS = "לחברי להב; רכישה דרך אתר המועדון"


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return style_platform.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
