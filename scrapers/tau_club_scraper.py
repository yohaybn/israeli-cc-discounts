"""Scraper for the אוניברסיטת תל אביב TAU benefits club (https://www.tauclub.co.il/).

The site runs on the uniq-club platform; benefits come from its public GraphQL endpoint
(shop 2) through uniq_platform. No login.
"""

import json
from typing import Any

import uniq_platform

SOURCE_KEY = "tau_club"
CLUB_NAME = "אוניברסיטת תל אביב TAU"
SITE_URL = "https://www.tauclub.co.il/"
SHOP_ID = "2"
LIMITATIONS = "לסטודנטים וחברי מועדון אוניברסיטת תל אביב"


def scrape(post=None) -> list[dict[str, Any]]:
    return uniq_platform.parse(uniq_platform.fetch_benefits(SHOP_ID, post), CLUB_NAME, SITE_URL, LIMITATIONS)


def fetch_raw(post=None) -> dict[str, str]:
    return {"benefits.json": json.dumps(uniq_platform.fetch_benefits(SHOP_ID, post), ensure_ascii=False)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
