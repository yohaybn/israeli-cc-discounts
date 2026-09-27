"""Public coupon tiles of מועדון האנרגיה on the Style platform."""

from typing import Callable
from scraper_utils import fetch_text
import style_coupon_clubs

SOURCE_KEY = "energy_club"
CLUB_NAME = "מועדון האנרגיה"
BASE_URL = "https://energy.style.co.il/"
LIMITATIONS = "לחברי מועדון האנרגיה; רכישה בכפוף לתנאי המועדון"

def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict]:
    return style_coupon_clubs.crawl(BASE_URL, CLUB_NAME, fetch, LIMITATIONS)

def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}
