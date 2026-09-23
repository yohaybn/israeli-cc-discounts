"""Shared crawler for club sites built on the "style" benefits platform.

Several Israeli benefit clubs (Shufersal 4U, כח לעובדים, עדיף, Hi-Benefit and others) run on
the same platform: the home page links category pages (``?page=category&id=N``) and each
category page shows benefit tiles linking to ``?page=Benefit&uuid=...``. Browsing is public;
login is only needed to buy. Three tile templates exist (``a.box-item`` with ``h4`` /
``p.description``, ``.product-title`` / ``.product-desciption``, and ``a.card.product`` with
``.product-title-bold`` / ``.product-title-regular`` / ``button.add-button``); all are handled.

Benefit type: a tile whose button says "לרכישה" is something bought through the club site
(a voucher). Other tiles are discounts given at the business. Clubs that are a credit card
(e.g. קורפורייט) pass ``default_type="billing_discount"`` so those tiles are labeled as a card
discount instead of a voucher; all other clubs keep the historical "voucher" default.
"""

import re
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, saving_percent

CATEGORY_RE = re.compile(r"page=category&id=(\d+)")
UUID_RE = re.compile(r"uuid=([0-9A-Fa-f-]+)")
GENERIC_LABELS = {"צפיה בהטבות נוספות", "הצג הכל", ""}
BUY_LABEL = "לרכישה"
PERCENT_BUTTON_RE = re.compile(r"\d+(?:\.\d+)?\s*%\s*הנחה")


def category_links(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    found: dict[str, str] = {}
    for link in soup.select('a[href*="page=category"]'):
        match = CATEGORY_RE.search(link.get("href") or "")
        name = clean(link.get_text(" ", strip=True))
        if match and (match.group(1) not in found or found[match.group(1)] in GENERIC_LABELS):
            found[match.group(1)] = name
    return found


def _first_text(tile, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        node = tile.select_one(selector)
        if node:
            text = clean(node.get_text(" ", strip=True))
            if text:
                return text
    return ""


def tile_type(button_text: str, default_type: str = "voucher") -> str:
    """"לרכישה" means the benefit is bought on the club site (voucher); otherwise the club default."""
    return "voucher" if BUY_LABEL in (button_text or "") else default_type


def parse_category(
    html: str,
    base_url: str,
    club: str,
    category: str = "",
    limitations: str = "",
    default_type: str = "voucher",
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select('a[href*="page=Benefit"]'):
        title = _first_text(tile, ("h4", ".product-title", ".product-title-bold"))
        if not title:
            image = tile.select_one("img[alt]")
            title = clean(image.get("alt")) if image else ""
        if not title:
            continue
        description = _first_text(tile, ("p.description", ".product-desciption", ".product-description", ".product-title-regular"))
        button = _first_text(tile, (".add-button",))
        discount_type = tile_type(button, default_type)
        discount = description or title
        value = saving_percent(description)
        if discount_type != "voucher" and PERCENT_BUTTON_RE.search(button):
            # card template: the button carries the discount ("5% הנחה"), the description the offer
            discount = f"{button} - {description}" if description else button
            value = saving_percent(button)
        elif discount_type != "voucher" and value is None and saving_percent(title) is not None:
            # e.g. title "15% הנחה ב- AVIS" with a plain description: keep the percent visible
            discount = f"{title} - {description}" if description else title
            value = saving_percent(title)
        href = urljoin(base_url, tile.get("href"))
        match = UUID_RE.search(href)
        url = urljoin(base_url, f"?page=Benefit&uuid={match.group(1)}") if match else href
        record = {
            "club": club,
            "business_name": title,
            "discount": discount,
            "discount_url": url,
            "discount_type": discount_type,
            "discount_value": value,
            "has_physical_store": True,
            "branches": [],
            "limitations": limitations,
        }
        if category and category not in GENERIC_LABELS:
            record["category"] = category
        records.append(record)
    return records


def crawl(
    base_url: str,
    club: str,
    fetch: Callable[[str], str],
    limitations: str = "",
    default_type: str = "voucher",
) -> list[dict[str, Any]]:
    queue = category_links(fetch(base_url))
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    while queue:
        cat_id, name = queue.popitem()
        if cat_id in seen:
            continue
        seen.add(cat_id)
        try:
            html = fetch(urljoin(base_url, f"?page=category&id={cat_id}"))
        except Exception as exc:  # one category should not sink the run
            print(f"WARNING: {base_url} category {cat_id} failed: {exc}")
            continue
        records.extend(parse_category(html, base_url, club, name, limitations, default_type))
        for sub_id, sub_name in category_links(html).items():
            if sub_id not in seen and sub_id not in queue:
                queue[sub_id] = sub_name
    by_url: dict[str, dict[str, Any]] = {}
    for record in records:
        existing = by_url.get(record["discount_url"])
        if existing is None or ("category" not in existing and "category" in record):
            by_url[record["discount_url"]] = record
    return dedupe(list(by_url.values()))
