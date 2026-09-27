"""Public coupon tiles of עובדי נמל אשדוד on the Style platform."""

from typing import Callable
from scraper_utils import fetch_text
import style_coupon_clubs

SOURCE_KEY = "ashdod_port"
CLUB_NAME = "עובדי נמל אשדוד"
BASE_URL = "https://ap.mycorporate.co.il/"
LIMITATIONS = "לעובדי נמל אשדוד; רכישה בכפוף לתנאי מועדון הקורפורייט"

def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict]:
    return style_coupon_clubs.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS)

def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}
