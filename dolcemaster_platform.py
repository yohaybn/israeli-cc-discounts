"""Shared crawler for club sites built on the dolcemaster benefits platform (e.g. טוב+).

Category pages (``/category/<id>``) are public and embed the full page state as
``window.__PRELOADED_STATE__``: the category tree under ``config.categories`` and up to 1000
products of the current category under ``config.category.products``. A category that has more
products (``has_more == "Y"``) is covered by crawling its sub-categories as well.
"""

import json
from typing import Any, Callable, Iterable

from scraper_utils import clean, html_to_text

STATE_MARKER = "window.__PRELOADED_STATE__ ="
GENERIC_TEXT = {"הטבת פלוס", "הטבה", ""}


def page_state(html: str) -> dict[str, Any]:
    start = (html or "").find(STATE_MARKER)
    if start < 0:
        raise ValueError("no preloaded state in page")
    state, _ = json.JSONDecoder().raw_decode(html[start + len(STATE_MARKER):].lstrip())
    return state.get("config") or {}


def category_tree(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in config.get("categories") or [] if c.get("require_login") != "Y"]


def _price(value: Any) -> float | None:
    try:
        price = float(value)
    except (TypeError, ValueError):
        return None
    return price if price > 0 else None


def benefit_text(product: dict[str, Any]) -> tuple[str, float | None]:
    club = _price(product.get("club_price"))
    market = _price(product.get("market_price")) or _price(product.get("discounted_price"))
    note = html_to_text(product.get("short_description"))
    parts = []
    percent = None
    if club and market and market > club:
        percent = round((market - club) / market * 100)
        parts.append(f"{club:g} ₪ במקום {market:g} ₪ ({percent}% חיסכון)")
    elif club:
        parts.append(f"מחיר חבר {club:g} ₪")
    if note and note not in GENERIC_TEXT:
        parts.append(note)
    return " - ".join(parts), (float(percent) if percent else None)


def crawl(base_url: str, seed_category_id: Any, fetch: Callable[[str], str]) -> list[dict[str, Any]]:
    """Return the unique products of all public categories of a dolcemaster club site.

    The crawl starts from a known public category page (the home page sits behind a bot
    challenge on some sites, while category pages carry the same category tree).
    """
    base = base_url.rstrip("/")
    products: dict[Any, dict[str, Any]] = {}
    seen: set[Any] = set()

    def visit(category_id: Any) -> dict[str, Any] | None:
        if category_id in seen:
            return None
        seen.add(category_id)
        try:
            config = page_state(fetch(f"{base}/category/{category_id}"))
        except Exception:
            return None
        category = config.get("category") or {}
        for product in category.get("products") or []:
            products.setdefault(product.get("product_id"), product)
        return {"config": config, "has_more": category.get("has_more") == "Y"}

    first = visit(seed_category_id)
    tree = category_tree(first["config"]) if first else []
    for top in tree:
        result = visit(top.get("category_id"))
        if result and result["has_more"]:
            for sub in _children(top):
                visit(sub.get("category_id"))
    return list(products.values())


def _children(category: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for child in category.get("categories") or []:
        if child.get("require_login") != "Y" and child.get("category_id") != category.get("category_id"):
            yield child


def product_name(product: dict[str, Any]) -> str:
    return clean(product.get("name"))
