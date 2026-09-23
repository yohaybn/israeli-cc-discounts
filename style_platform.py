"""Shared crawler for club sites built on the "style" benefits platform.

Several Israeli benefit clubs (Shufersal 4U, כח לעובדים, עדיף, Hi-Benefit and others) run on
the same platform: the home page links category pages (``?page=category&id=N``) and each
category page shows benefit tiles linking to ``?page=Benefit&uuid=...``. Browsing is public;
login is only needed to buy. Two tile templates exist (``a.box-item`` with ``h4`` /
``p.description``, and ``.product-title`` / ``.product-desciption``); both are handled.
"""

import re
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, saving_percent

CATEGORY_RE = re.compile(r"page=category&id=(\d+)")
UUID_RE = re.compile(r"uuid=([0-9A-Fa-f-]+)")
GENERIC_LABELS = {"צפיה בהטבות נוספות", "הצג הכל", ""}


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


def parse_category(html: str, base_url: str, club: str, category: str = "", limitations: str = "") -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    records = []
    for tile in soup.select('a[href*="page=Benefit"]'):
        title = _first_text(tile, ("h4", ".product-title"))
        if not title:
            image = tile.select_one("img[alt]")
            title = clean(image.get("alt")) if image else ""
        if not title:
            continue
        description = _first_text(tile, ("p.description", ".product-desciption", ".product-description"))
        href = urljoin(base_url, tile.get("href"))
        match = UUID_RE.search(href)
        url = urljoin(base_url, f"?page=Benefit&uuid={match.group(1)}") if match else href
        record = {
            "club": club,
            "business_name": title,
            "discount": description or title,
            "discount_url": url,
            "discount_type": "voucher",
            "discount_value": saving_percent(description),
            "has_physical_store": True,
            "branches": [],
            "limitations": limitations,
        }
        if category and category not in GENERIC_LABELS:
            record["category"] = category
        records.append(record)
    return records


def crawl(base_url: str, club: str, fetch: Callable[[str], str], limitations: str = "") -> list[dict[str, Any]]:
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
        records.extend(parse_category(html, base_url, club, name, limitations))
        for sub_id, sub_name in category_links(html).items():
            if sub_id not in seen and sub_id not in queue:
                queue[sub_id] = sub_name
    by_url: dict[str, dict[str, Any]] = {}
    for record in records:
        existing = by_url.get(record["discount_url"])
        if existing is None or ("category" not in existing and "category" in record):
            by_url[record["discount_url"]] = record
    return dedupe(list(by_url.values()))
