"""Scraper for the IMA "Yahad" members club (מועדון יחד של ההסתדרות הרפואית).

The club catalog at https://www.ima.org.il/yahadclub/Categories.aspx is public (no login).
Categories link to Suppliers.aspx?CategoryId=..., which lists suppliers linking to
SupplierDetails.aspx?supId=..., where the discount text and branch table live. The site is
an old ASP.NET app, so requests run one at a time.
"""

import re
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


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    categories = parse_categories(fetch(CATEGORIES_URL))
    supplier_category: dict[str, str] = {}
    for cat_id, cat_name in categories.items():
        try:
            html = fetch(urljoin(BASE_URL, f"Suppliers.aspx?CategoryId={cat_id}"))
        except Exception as exc:  # one slow category should not sink the run
            print(f"WARNING: category {cat_id} failed: {exc}")
            continue
        for sup_id in parse_supplier_list(html):
            supplier_category.setdefault(sup_id, cat_name)
    records = []
    for sup_id, cat_name in supplier_category.items():
        try:
            html = fetch(urljoin(BASE_URL, f"SupplierDetails.aspx?supId={sup_id}"))
        except Exception as exc:
            print(f"WARNING: supplier {sup_id} failed: {exc}")
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
