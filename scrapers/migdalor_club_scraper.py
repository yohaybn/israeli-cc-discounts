"""Public coupon tiles of עמותת מגדלור on the Style platform."""

from typing import Callable
from scraper_utils import fetch_text
import style_coupon_clubs

SOURCE_KEY = "migdalor_club"
CLUB_NAME = "עמותת מגדלור"
BASE_URL = "https://migdalor.style.co.il/"
LIMITATIONS = "לחברי עמותת מגדלור; רכישה בכפוף לתנאי המועדון"

def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict]:
    return style_coupon_clubs.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS)

def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}
