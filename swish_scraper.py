"""Scraper for businesses that accept the Swish Plus gift card.

The public product page https://swish.co.il/home/fashion-and-style-giftcard/product-105380
(no login) is a Next.js page. Its React Server Components payload embeds the full
"where to use" list under "tagsChains" -> "chainsByWallet". This module decodes that
payload and turns each chain into a discount record.
"""

import json
import re
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, html_to_text

SOURCE_KEY = "swish"
CLUB_NAME = "Swish Plus"
PAGE_URL = "https://swish.co.il/home/fashion-and-style-giftcard/product-105380"
DISCOUNT_TEXT = "מכבד את גיפט קארד Swish Plus"
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


def chain_to_record(chain: dict[str, Any]) -> dict[str, Any] | None:
    name = clean(chain.get("storeName"))
    if not name:
        return None
    category = clean(chain.get("tagName"))
    notes = html_to_text(chain.get("mustToKnow") or "")
    limitations = " | ".join(part for part in (f"קטגוריה: {category}" if category else "", notes) if part)
    return {
        "club": CLUB_NAME,
        "business_name": name,
        "discount": DISCOUNT_TEXT,
        "discount_url": clean(chain.get("webSite")) or PAGE_URL,
        "discount_type": "gift_card",
        "discount_value": None,
        "has_physical_store": category != ONLINE_TAG,
        "branches": [],
        "limitations": limitations,
    }


def parse_page(html: str) -> list[dict[str, Any]]:
    records = [chain_to_record(chain) for chain in extract_chains(html)]
    return dedupe([record for record in records if record])


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"swish_plus.html": fetch(PAGE_URL)}


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    return parse_page(fetch(PAGE_URL))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} businesses")
    for item in items[:3]:
        print(item)
