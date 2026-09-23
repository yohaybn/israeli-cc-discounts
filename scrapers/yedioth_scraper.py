"""Scraper for the public benefits page of the Yedioth Ahronoth subscribers club."""

from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, is_online_only, percent_value

SOURCE_KEY = "yedioth"
CLUB_NAME = "ידיעות אחרונות"
SOURCE_URL = "https://www.yedioth.co.il/"


def parse_yedioth_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for box in soup.select("a.benefits-box[href]"):
        title = box.select_one(".title")
        subtitle = box.select_one(".subTitle")
        name = clean(title.get_text(" ", strip=True) if title else box.get("title", ""))
        discount = clean(subtitle.get_text(" ", strip=True) if subtitle else "")
        if not name or not discount:
            continue
        if discount == name:
            discount = f"הטבה למנויי ידיעות אחרונות: {name}"
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": discount,
            "discount_url": urljoin(SOURCE_URL, box["href"].strip()),
            "discount_type": "voucher",
            "discount_value": percent_value(discount),
            "has_physical_store": not is_online_only(discount),
            "branches": [],
            "limitations": "למנויי ידיעות אחרונות",
        })
    return dedupe(records)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"homepage.html": fetch(SOURCE_URL)}


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse_yedioth_html(fetch(SOURCE_URL))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:5]:
        print(item)
