"""Scraper for the IMA "Yahad" members club (מועדון יחד של ההסתדרות הרפואית).

The club catalog at https://www.ima.org.il/yahadclub/Categories.aspx is public (no login).
Categories link to Suppliers.aspx?CategoryId=..., which lists suppliers linking to
SupplierDetails.aspx?supId=..., where the discount text and branch table live. The site is
an old ASP.NET app: pages are fetched by a small bounded thread pool (MAX_WORKERS, default 6,
override with IMA_YAHAD_WORKERS) instead of one at a time, which took ~35 minutes.
"""

import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, fetch_text, percent_value

SOURCE_KEY = "ima_yahad"
CLUB_NAME = "מועדון יחד - ההסתדרות הרפואית"
BASE_URL = "https://www.ima.org.il/yahadclub/"
CATEGORIES_URL = urljoin(BASE_URL, "Categories.aspx")
CATEGORY_RE = re.compile(r"CategoryId=(\d+)")
SUPPLIER_RE = re.compile(r"supId=(\d+)")
MAX_WORKERS = max(1, int(os.environ.get("IMA_YAHAD_WORKERS", "6") or 6))


def _fetch_all(fetch: Callable[[str], str], urls: list[str], workers: int) -> list[str | None]:
    """Fetch URLs concurrently, keeping input order; a failed page becomes None."""
    def one(url: str) -> str | None:
        try:
            return fetch(url)
        except Exception as exc:  # one slow page should not sink the run
            print(f"WARNING: {url} failed: {exc}")
            return None

    if workers <= 1 or len(urls) <= 1:
        return [one(url) for url in urls]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, urls))


def parse_categories(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    categories: dict[str, str] = {}
    for link in soup.select('a[href*="CategoryId="]'):
        match = CATEGORY_RE.search(link.get("href") or "")
        name = clean(link.get_text(" ", strip=True) or link.get("title"))
        if match and match.group(1) not in categories:
            categories[match.group(1)] = name
    return categories


def parse_supplier_list(html: str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    ids = []
    for link in soup.select("a[id$=hylName]"):
        match = SUPPLIER_RE.search(link.get("href") or "")
        if match and match.group(1) not in ids:
            ids.append(match.group(1))
    return ids


def _text(soup: BeautifulSoup, suffix: str) -> str:
    node = soup.select_one(f"[id$={suffix}]")
    return clean(node.get_text(" ", strip=True)) if node else ""


def parse_supplier(html: str, sup_id: str, category: str = "") -> dict[str, Any] | None:
    soup = BeautifulSoup(html or "", "html.parser")
    name = _text(soup, "lblName")
    discount = _text(soup, "lblDiscount")
    if not name or not discount:
        return None
    branches = []
    for row in soup.select("[id$=dvBranches] .supplierBranches"):
        branch = {
            "address": _text(row, "lblAddress"),
            "city": _text(row, "lblCity"),
            "phone": _text(row, "lblPhoneNum"),
        }
        website = row.select_one("a[id$=hylWebSite]")
        if website and clean(website.get("href")):
            branch["website"] = clean(website.get("href"))
        if any(branch.values()):
            branches.append(branch)
    description = _text(soup, "lblDescription")
    record = {
        "club": CLUB_NAME,
        "business_name": name,
        "discount": discount,
        "discount_url": urljoin(BASE_URL, f"SupplierDetails.aspx?supId={sup_id}"),
        "discount_type": "club_card",
        "discount_value": percent_value(discount),
        "has_physical_store": any(b.get("address") or b.get("city") for b in branches),
        "branches": branches,
        "limitations": description,
    }
    if category:
        record["category"] = category
    return record


def scrape(fetch: Callable[[str], str] = fetch_text, workers: int | None = None) -> list[dict[str, Any]]:
    workers = MAX_WORKERS if workers is None else workers
    categories = parse_categories(fetch(CATEGORIES_URL))
    cat_items = list(categories.items())
    pages = _fetch_all(fetch, [urljoin(BASE_URL, f"Suppliers.aspx?CategoryId={cid}") for cid, _ in cat_items], workers)
    supplier_category: dict[str, str] = {}
    for (_, cat_name), html in zip(cat_items, pages):
        if html is None:
            continue
        for sup_id in parse_supplier_list(html):
            supplier_category.setdefault(sup_id, cat_name)
    sup_items = list(supplier_category.items())
    details = _fetch_all(fetch, [urljoin(BASE_URL, f"SupplierDetails.aspx?supId={sid}") for sid, _ in sup_items], workers)
    records = []
    for (sup_id, cat_name), html in zip(sup_items, details):
        if html is None:
            continue
        record = parse_supplier(html, sup_id, cat_name)
        if record:
            records.append(record)
    return records


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"categories.html": fetch(CATEGORIES_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} suppliers")
    for item in items[:3]:
        print(item)
