"""Scraper for רשף - retired firefighters' association (https://reshef102.org/benefits/).

The public benefits page is an Elementor grid of image tiles: each ``<figure>`` links to the
partner and has the partner name in its ``<figcaption>``. Some tiles are other benefit clubs the
members belong to; they are kept and labelled as such.
"""

import html as htmllib
import re
from typing import Any, Callable

from scraper_utils import dedupe, fetch_text, html_to_text

SOURCE_KEY = "reshef"
CLUB_NAME = "רשף - גמלאי כבאות והצלה"
URL = "https://reshef102.org/benefits/"
LIMITATIONS = "לחברי עמותת רשף (גמלאי כבאות והצלה) ובני משפחותיהם"
FIGURE_RE = re.compile(r"<figure[^>]*>(.*?)</figure>", re.S)
HREF_RE = re.compile(r'<a[^>]+href="([^"]+)"')
CAPTION_RE = re.compile(r"<figcaption[^>]*>(.*?)</figcaption>", re.S)
CLUB_WORDS = ("מועדון", "מולטיפאס")


def _link(href: str) -> str:
    href = htmllib.unescape(href or "")
    if not href.startswith("http") or "bing.com/" in href:
        return URL
    return href


def parse(html: str) -> list[dict[str, Any]]:
    records = []
    for figure in FIGURE_RE.findall(html or ""):
        caption = CAPTION_RE.search(figure)
        name = html_to_text(caption.group(1)) if caption else ""
        if not name:
            continue
        href = HREF_RE.search(figure)
        is_club = any(word in name for word in CLUB_WORDS)
        records.append({
            "club": CLUB_NAME,
            "business_name": name,
            "discount": ("הטבות דרך מועדון שותף: " if is_club else "הסדר/הנחה לחברי רשף: ") + name,
            "discount_url": _link(href.group(1) if href else ""),
            "discount_type": "club_card" if is_club else "discount",
            "discount_value": None,
            "has_physical_store": True,
            "branches": [],
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse(fetch(URL))


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"benefits.html": fetch(URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} benefits")
    for item in items:
        print(item["discount_type"], item["business_name"], item["discount_url"][:60])
