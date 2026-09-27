"""Conservative public coupon crawler for Style-powered worker/association clubs.

Ordinary merchandise and card-on-billing discounts are not coupons. A purchase tile
must describe a voucher or a service/experience; a price or voucher saving must be
published. This uses only unauthenticated category HTML, never member endpoints.
"""

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper_utils import clean, dedupe, fetch_text, saving_percent
from style_platform import category_links, UUID_RE

PRICE_RE = re.compile(r"(?:לרכישה\s*)?ב-?\s*₪\s*([\d,.]+)\s*(?:בשווי|במקום)\s*₪\s*([\d,.]+)")
VOUCHER_RE = re.compile(r"שובר|תו\s*(?:קנייה|שי|מתנה|פלוס)|כרטיס|קופון|קרדיט|gift\s*card", re.I)
SERVICE_CATEGORIES = {"7", "68", "37", "25", "32"}  # food, restaurants, attractions, travel, culture
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*%\s*הנחה")


def parse_category(html: str, base_url: str, club: str, category_id: str, category: str,
                   limitations: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for tile in soup.select('a[href*="page=Benefit"]'):
        href = urljoin(base_url, tile.get("href") or "")
        uuid = UUID_RE.search(href)
        if not uuid:
            continue
        title_node = tile.select_one(".product-title,.product-title-bold,h4")
        desc_node = tile.select_one(".product-desciption,.product-description,p.description,.product-title-regular")
        button_node = tile.select_one(".product-price,.add-button")
        title = clean(title_node.get_text(" ", strip=True)) if title_node else ""
        description = clean(desc_node.get_text(" ", strip=True)) if desc_node else ""
        button = clean(button_node.get_text(" ", strip=True)) if button_node else ""
        if not title or button != "לרכישה":  # "לפרטים" and percentages are not coupon checkout
            continue
        is_voucher = bool(VOUCHER_RE.search(title + " " + description))
        is_service = category_id in SERVICE_CATEGORIES
        if not (is_voucher or is_service):
            continue
        price, original_price = None, None
        match = PRICE_RE.search(description)
        if match:
            try:
                price, original_price = (float(n.replace(",", "")) for n in match.groups())
            except ValueError:
                continue
            if not 0 < price < original_price:
                continue
            value = round((original_price - price) / original_price * 100, 1)
        elif is_voucher and PERCENT_RE.search(description):
            value = saving_percent(description)
        else:
            continue
        record = {
            "club": club, "business_name": title, "discount": description,
            "discount_url": urljoin(base_url, f"?page=Benefit&uuid={uuid.group(1)}"),
            "discount_type": "coupon", "discount_value": value,
            "voucher_type": "voucher" if is_voucher else "experience",
            "has_physical_store": True, "branches": [], "limitations": limitations,
            "category": category,
        }
        if price is not None:
            record.update(price=price, original_price=original_price)
        records.append(record)
    return records


def crawl(base_url: str, club: str, fetch: Callable[[str], str] = fetch_text,
          limitations: str = "") -> list[dict]:
    categories = category_links(fetch(base_url))
    if not categories or len(categories) > 100:
        raise ValueError("missing or excessive public categories")
    queue = [(cat_id, name, cat_id) for cat_id, name in categories.items()]
    seen = set()
    records = []
    while queue:
        batch = list(dict((cat_id, (name, root_id)) for cat_id, name, root_id in queue if cat_id not in seen).items())
        queue = []
        if len(seen) + len(batch) > 100:
            raise ValueError("public category limit exceeded")
        def read(entry):
            cat_id, (name, root_id) = entry
            html = fetch(urljoin(base_url, f"?page=category&id={cat_id}"))
            if "page=category" not in html or "page=Benefit" not in html:
                raise ValueError(f"public category {cat_id} missing benefit tiles")
            return cat_id, root_id, parse_category(html, base_url, club, root_id, name, limitations), category_links(html)
        with ThreadPoolExecutor(max_workers=4) as pool:
            for cat_id, root_id, parsed, links in pool.map(read, batch):
                seen.add(cat_id)
                records.extend(parsed)
                for child_id, child_name in links.items():
                    if child_id not in seen and not any(x[0] == child_id for x in queue):
                        queue.append((child_id, child_name, root_id))
    unique = {}
    for row in records:
        unique.setdefault(row["discount_url"], row)
    if not unique:
        raise ValueError("public catalog produced no coupons")
    return dedupe(list(unique.values()))
