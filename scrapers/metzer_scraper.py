"""Scraper for the מצר benefits club (https://metzer.htzone.co.il/).

The site runs on the HTzone white-label platform, so the crawl is done by htzone_platform.crawl:
public category pages and a public ajax call, no login (login is only needed to buy).
"""

from typing import Any

import htzone_platform

SOURCE_KEY = "metzer"
CLUB_NAME = "מצר"
BASE_URL = "https://metzer.htzone.co.il/"
LIMITATIONS = "לחברי מועדון מצר; הנחות במעמד חיוב למשלמים בכרטיס האשראי של המועדון"


def scrape(fetch=None, post=None) -> list[dict[str, Any]]:
    if fetch is None or post is None:
        fetch, post = htzone_platform.make_session_io()
    return htzone_platform.crawl(BASE_URL, CLUB_NAME, fetch, post, LIMITATIONS)


def fetch_raw(fetch=None) -> dict[str, str]:
    if fetch is None:
        fetch, _ = htzone_platform.make_session_io()
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
