"""Scraper for the Hi-Benefit - לשכת רואי החשבון benefits club (https://www.benefit-icpas.co.il/).

The site runs on the shared "style" benefits platform, so the crawl is done by
style_platform.crawl: public category pages, no login (login is only needed to buy).
"""

from typing import Any, Callable

import style_platform
from scraper_utils import fetch_text

SOURCE_KEY = "hibenefit"
CLUB_NAME = "Hi-Benefit - לשכת רואי החשבון"
BASE_URL = "https://www.benefit-icpas.co.il/"
LIMITATIONS = "למחזיקי כרטיס Hi-Benefit של לשכת רואי החשבון; רכישה דרך אתר המועדון"


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return style_platform.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
