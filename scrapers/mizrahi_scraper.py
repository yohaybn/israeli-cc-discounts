"""Scraper for the public benefits catalog of Mizrahi-Tefahot's club ("הכרטיס")."""

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, is_online_only, percent_value

SOURCE_KEY = "mizrahi"
CLUB_NAME = "מזרחי טפחות"
SOURCE_URL = "https://www.mizrahi-tefahot.co.il/hacartis/all/"

CATEGORY_NAMES = {
    "culture": "תרבות ופנאי",
    "tourism": "תיירות",
    "holidays": "חופשות",
    "restautants": "מסעדות",
    "fashion": "אופנה",
    "insurance": "ביטוח",
    "elctricity": "חשמל",
    "home-garden": "בית וגן",
    "katom-max": "כתום MAX",
}


def _first_text(node, *selectors: str) -> str:
    for selector in selectors:
        found = node.select_one(selector)
        if found:
            text = clean(found.get_text(" ", strip=True))
            if text:
                return text
    return ""


def parse_mizrahi_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []
    for anchor in soup.select("a.hatava[href]"):
        href = anchor["href"].strip()
        name = _first_text(anchor, ".name .hidden-mobile", ".name")
        discount = _first_text(anchor, ".desc.hidden-mobile", ".desc")
        aria = clean(anchor.get("aria-label") or "")
        if aria.startswith("למימוש ההטבה -"):
            full = clean(aria.split("-", 1)[1])
            if len(full) > len(discount):
                discount = full
        if discount.endswith("..."):
            full = _first_text(anchor, ".desc.visible-xs-mobile")
            if full:
                discount = full
        if not name or not discount:
            continue
        percent_text = _first_text(anchor, ".percents")
        value = percent_value(percent_text) or percent_value(discount)
        if value is not None and percent_text and percent_text not in discount:
            discount = f"{percent_text} הנחה - {discount}"
        segments = [part for part in href.split("/") if part]
        category = CATEGORY_NAMES.get(segments[1], segments[1]) if len(segments) > 2 else ""
        coupon = bool(anchor.select_one(".coupon-code"))
        record = {
            "club": CLUB_NAME,
            "business_name": name,
            "discount": discount,
            "discount_url": urljoin(SOURCE_URL, href),
            "discount_type": "billing_discount",
            "discount_value": value,
            "has_physical_store": not is_online_only(discount),
            "branches": [],
            "limitations": "קוד הטבה" if coupon else "",
        }
        if category:
            record["category"] = category
        records.append(record)
    return dedupe(records)


def fetch_raw() -> dict[str, str]:
    return {"all_benefits.html": fetch_text(SOURCE_URL)}


def scrape() -> list[dict[str, Any]]:
    return parse_mizrahi_html(fetch_text(SOURCE_URL))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items[:5]:
        print(item)
