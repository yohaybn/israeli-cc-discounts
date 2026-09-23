"""Scraper for the volunteer benefits club of איחוד הצלה (https://4u.1221.org.il/).

The club site is WooCommerce and every benefit is a product. The public WooCommerce Store API
(``/wp-json/wc/store/v1/products``) lists them without login. The benefit line is picked from the
product's short description (the first line that names a discount, price or percent).
"""

import json
import re
from html import unescape
from typing import Any, Callable

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, is_online_only, percent_value

SOURCE_KEY = "ihud_hatzala"
CLUB_NAME = "איחוד הצלה"
BASE_URL = "https://4u.1221.org.il/"
API_URL = BASE_URL + "wp-json/wc/store/v1/products"
PER_PAGE = 100
MAX_PAGES = 20
LIMITATIONS = "למתנדבי ועובדי איחוד הצלה; בהצגת כרטיס מתנדב או קוד מהאתר"
EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u200d]+")
OFFER = re.compile(r"%|הנחה|₪|מתנה|חינם|במחיר")
GENERIC = re.compile(r"צוות רווחת|שמח להציג|מתנדבי.*היקרים")


def _lines(html: str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text("\n")
    return [c for c in (clean(EMOJI.sub(" ", unescape(line))) for line in text.split("\n")) if len(c) > 2]


def benefit_line(html: str) -> str:
    lines = [line for line in _lines(html) if not GENERIC.search(line)]
    for line in lines:
        if OFFER.search(line):
            return line
    return lines[0] if lines else ""


def parse(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in items:
        name = clean(unescape(item.get("name") or ""))
        if not name:
            continue
        text = benefit_line(item.get("short_description") or "") or benefit_line(item.get("description") or "") or name
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": text,
            "discount_url": item.get("permalink") or BASE_URL,
            "discount_type": "voucher",
            "discount_value": percent_value(text),
            "has_physical_store": not is_online_only(text),
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def fetch_products(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        batch = json.loads(fetch(f"{API_URL}?per_page={PER_PAGE}&page={page}"))
        if not batch:
            break
        items.extend(batch)
        if len(batch) < PER_PAGE:
            break
    return items


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch_products(fetch))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"products.json": fetch(f"{API_URL}?per_page={PER_PAGE}&page=1")}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:3]:
        print(item)
