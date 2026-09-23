"""Scraper for businesses that accept the multi-brand Swish (נופשונית) gift cards.

Covers the cards that Fid lists as clubs: Swish Plus, Perfect, Premium, Unique and Baby.
Each card has a public product page on swish.co.il (no login), a Next.js page. Its React Server Components payload embeds the full
"where to use" list under "tagsChains" -> "chainsByWallet". This module decodes that
payload and turns each chain into a discount record.
"""

import json
import re
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, html_to_text

SOURCE_KEY = "swish"
CLUB_NAME = "Swish"
# card name -> public product page
CARDS = {
    "Swish Plus": "https://swish.co.il/home/fashion-and-style-giftcard/product-105380",
    "Swish Perfect": "https://swish.co.il/business/all-gifts-giftcard/product-103980",
    "Swish Premium": "https://swish.co.il/business/all-gifts-giftcard/product-104068",
    "Swish Unique": "https://swish.co.il/business/all-gifts-giftcard/product-72261",
    "Swish Baby": "https://swish.co.il/home/birth-giftcard/product-95963",
}
PAGE_URL = CARDS["Swish Plus"]
ONLINE_TAG = "רכישה אונליין"
PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')


def extract_chains(html: str) -> list[dict[str, Any]]:
    payload = "".join(json.loads(chunk) for chunk in PUSH_RE.findall(html or ""))
    marker = '"tagsChains":'
    start = payload.find(marker)
    if start < 0:
        return []
    try:
        groups, _ = json.JSONDecoder().raw_decode(payload[start + len(marker):])
    except ValueError:
        return []
    chains = []
    for group in groups if isinstance(groups, list) else []:
        for chain in (group or {}).get("chainsByWallet") or []:
            if isinstance(chain, dict):
                chains.append(chain)
    return chains


def chain_to_record(chain: dict[str, Any], card: str = "Swish Plus", page_url: str = PAGE_URL) -> dict[str, Any] | None:
    name = clean(chain.get("storeName"))
    if not name:
        return None
    category = clean(chain.get("tagName"))
    notes = html_to_text(chain.get("mustToKnow") or "")
    limitations = " | ".join(part for part in (f"קטגוריה: {category}" if category else "", notes) if part)
    return {
        "club": card,
        "business_name": name,
        "discount": f"מכבד את גיפט קארד {card}",
        "discount_url": clean(chain.get("webSite")) or page_url,
        "discount_type": "gift_card",
        "discount_value": None,
        "has_physical_store": category != ONLINE_TAG,
        "branches": [],
        "limitations": limitations,
    }


def parse_page(html: str, card: str = "Swish Plus", page_url: str = PAGE_URL) -> list[dict[str, Any]]:
    records = [chain_to_record(chain, card, page_url) for chain in extract_chains(html)]
    return dedupe([record for record in records if record])


def _slug(card: str) -> str:
    return card.lower().replace(" ", "_")


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {f"{_slug(card)}.html": fetch(url) for card, url in CARDS.items()}


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for card, url in CARDS.items():
        try:
            html = fetch(url)
        except Exception as exc:  # one card failing should not drop the others
            print(f"WARNING: {card} page failed: {exc}")
            continue
        records.extend(parse_page(html, card, url))
    return records


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} businesses")
    for item in items[:3]:
        print(item)
