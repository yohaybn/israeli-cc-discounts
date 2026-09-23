"""Scraper for the קורפורייט benefits club (https://www.mycorporate.co.il/).

The site runs on the shared "style" benefits platform, so the crawl is done by
style_platform.crawl: public category pages, no login (login is only needed to buy).

Corporate is an Isracard credit card: most benefits are an automatic discount when paying with
the club card ("5% הנחה אוטומטית למשלמים בכרטיס המועדון"), so they are ``billing_discount``.
Only tiles bought on the site ("לרכישה") are vouchers.
"""

from typing import Any, Callable

import style_platform
from scraper_utils import fetch_text

SOURCE_KEY = "corporate"
CLUB_NAME = "קורפורייט"
BASE_URL = "https://www.mycorporate.co.il/"
LIMITATIONS = "לחברי מועדון קורפורייט"
DISCOUNT_TYPE = "billing_discount"


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return style_platform.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS, default_type=DISCOUNT_TYPE)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
