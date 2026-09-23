#!/usr/bin/env python3
"""Scraper for MAX card discounts.

Endpoint: https://www.max.co.il/api/vgc/getCardsListShivuki
Scrapes cards from MAX, assigns discount types dynamically (rechargeable_card vs gift_card),
extracts participating stores, deduplicates them across cards and categories,
and formats them into standard normalized records.
"""

import argparse
import json
import logging
from typing import Any, Dict, List

import requests

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

MAX_API_URL = "https://www.max.co.il/api/vgc/getCardsListShivuki"
FALLBACK_URL = "https://www.max.co.il/gift-card-network"
DEFAULT_DISCOUNT_PERCENT = 16.0

# Card titles/keywords that represent rechargeable cards
RECHARGEABLE_KEYWORDS = ["executive", "giftcard max", "gift card max"]


def get_discount_type(card_title: str) -> str:
    """Determine discount type based on card title.

    'כרטיס הטבות executive' and 'GiftCard max' are rechargeable_card.
    All other cards are treated as gift_card.
    """
    title_lower = card_title.lower()
    for keyword in RECHARGEABLE_KEYWORDS:
        if keyword in title_lower:
            return "rechargeable_card"
    return "gift_card"


def fetch_max_cards(url: str = MAX_API_URL) -> Dict[str, Any]:
    """Fetch raw JSON payload from MAX API endpoint."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_max_payload(
    payload: Dict[str, Any],
    discount_value: float = DEFAULT_DISCOUNT_PERCENT,
) -> List[Dict[str, Any]]:
    """Parse MAX JSON payload into normalized discount records.

    Deduplicates stores based on Hebrew chain name/title and card discount type.
    """
    result = payload.get("Result", {})
    cards = result.get("Cards", [])

    if not cards:
        LOGGER.warning("No cards found in MAX response payload.")
        return []

    stores_map: Dict[str, Dict[str, Any]] = {}

    for card in cards:
        card_title = card.get("Title") or card.get("CardNameForMaxApp") or "GiftCard max"
        discount_type = get_discount_type(card_title)
        
        # Calculate discount string and numerical value based on card type
        if discount_type == "rechargeable_card":
            current_discount_value = discount_value
            discount_str = f"{int(discount_value) if discount_value.is_integer() else discount_value}%"
        else:
            current_discount_value = 0.0
            discount_str = " gift_card"

        card_categories = card.get("Stores", [])

        for cat_entry in card_categories:
            category_name = cat_entry.get("StoresCategory") or ""
            category_english = cat_entry.get("StoresCategoryEnglish") or ""
            is_online_category = (
                "אונליין" in category_name or "Online" in category_english
            )

            store_list = cat_entry.get("Stores", [])
            for s in store_list:
                chain_hebrew = (s.get("ChainNameHebrew") or "").strip()
                title = (s.get("Title") or "").strip()

                name = f'{chain_hebrew} {"-" if chain_hebrew and title else ""} {title}'.strip()
                if not name:
                    continue

                # Use ChainUrl if provided, otherwise default to FALLBACK_URL
                chain_url = (s.get("ChainUrl") or "").strip()
                discount_url = chain_url if chain_url else FALLBACK_URL

                # Key by normalized lower name and discount type to handle deduplication per store type
                dedup_key = f"{name.lower()}::{discount_type}"

                if dedup_key not in stores_map:
                    stores_map[dedup_key] = {
                        "club": card_title,
                        "business_name": name,
                        "discount": f'{card_title} | {discount_str}',
                        "discount_url": discount_url,
                        "discount_type": discount_type,
                        "discount_value": current_discount_value,
                        "card_names": set([card_title]),
                        "categories": set([category_name]) if category_name else set(),
                        "is_online_only": is_online_category,
                    }
                else:
                    item = stores_map[dedup_key]
                    item["card_names"].add(card_title)
                    if category_name:
                        item["categories"].add(category_name)
                    if not is_online_category:
                        item["is_online_only"] = False

    normalized_records = []
    for item in stores_map.values():
        record = {
            "club": item["club"],
            "business_name": item["business_name"],
            "discount": item["discount"],
            "discount_url": item["discount_url"],
            "discount_type": item["discount_type"],
            "discount_value": item["discount_value"],
            "has_physical_store": not item["is_online_only"],
        }
        normalized_records.append(record)

    return normalized_records


def scrape_max(
    url: str = MAX_API_URL,
    discount_value: float = DEFAULT_DISCOUNT_PERCENT,
) -> List[Dict[str, Any]]:
    """Scrape MAX cards and return a normalized list of discount records."""
    LOGGER.info("Fetching MAX cards list from %s", url)
    try:
        payload = fetch_max_cards(url)
    except Exception as e:
        LOGGER.error("Failed to fetch MAX cards data: %s", e)
        return []

    discounts = parse_max_payload(payload, discount_value=discount_value)
    LOGGER.info("Extracted %d normalized discounts for MAX", len(discounts))
    return discounts


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape MAX card discounts")
    parser.add_argument("--json-file", help="Path to local JSON response file (optional)")
    parser.add_argument(
        "--discount",
        type=float,
        default=DEFAULT_DISCOUNT_PERCENT,
        help="Discount percentage for rechargeable cards (default: 16)",
    )
    args = parser.parse_args()

    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        discounts = parse_max_payload(payload, discount_value=args.discount)
    else:
        discounts = scrape_max(discount_value=args.discount)

    preview = discounts[:5]
    print(f"Extracted {len(discounts)} total stores. Preview of first {len(preview)} entries:")
    print(json.dumps(preview, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()