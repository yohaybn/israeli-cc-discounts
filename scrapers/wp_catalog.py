"""Helpers for gift-card networks that publish their store list through the public WordPress REST API."""

import json
from typing import Any, Callable

from scraper_utils import clean, fetch_text, html_to_text
from html import unescape

MAX_PAGES = 20


def fetch_wp_collection(base_url: str, endpoint: str, fields: str, fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    """Read every page of a public `/wp-json/wp/v2/<endpoint>` collection."""
    items: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        url = f"{base_url.rstrip('/')}/wp-json/wp/v2/{endpoint}?per_page=100&page={page}&_fields={fields}"
        try:
            payload = json.loads(fetch(url))
        except Exception:
            if page == 1:
                raise
            break  # WordPress answers 400 past the last page
        if not isinstance(payload, list) or not payload:
            break
        items.extend(item for item in payload if isinstance(item, dict))
        if len(payload) < 100:
            break
    return items


def term_names(terms: list[dict[str, Any]]) -> dict[int, str]:
    return {term["id"]: clean(unescape(term.get("name") or "")) for term in terms if "id" in term}


def rendered(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if isinstance(value, dict):
        value = value.get("rendered")
    return html_to_text(unescape(value or ""))
