"""Scraper for MY OFER, the Ofer malls customer club (קניוני עופר / MyOfer).

The public deals page of each mall, https://myofer.co.il/malls/<mall>/deals?page=N (no login),
is a Next.js page whose __NEXT_DATA__ holds 10 deals per page plus the total count. The mall
list comes from the home page's __NEXT_DATA__. Many deals repeat across malls, so records are
merged by deal id and list every mall they appear in.
"""

import json
import math
import re
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, html_to_text, saving_percent

SOURCE_KEY = "myofer"
CLUB_NAME = "MY OFER - קניוני עופר"
BASE_URL = "https://myofer.co.il/"
PAGE_SIZE = 10
MAX_PAGES = 60
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def page_props(html: str) -> dict[str, Any]:
    match = NEXT_DATA_RE.search(html or "")
    if not match:
        return {}
    try:
        return json.loads(match.group(1)).get("props", {}).get("pageProps", {}) or {}
    except ValueError:
        return {}


def parse_malls(html: str) -> list[dict[str, str]]:
    malls = []
    for mall in page_props(html).get("malls") or []:
        slug = clean(mall.get("seoTitle"))
        if slug:
            malls.append({"slug": slug, "name": clean(mall.get("name")) or slug})
    return malls


def deals_url(slug: str, page: int = 1) -> str:
    url = f"{BASE_URL}malls/{slug}/deals"
    return url if page <= 1 else f"{url}?page={page}"


def deal_to_record(deal: dict[str, Any], mall: dict[str, str]) -> dict[str, Any] | None:
    store = deal.get("store") or {}
    details = deal.get("details") or {}
    name = clean(store.get("name"))
    title = clean(details.get("title"))
    if not name or not title or deal.get("isActive") is False:
        return None
    subtitle = clean(details.get("subtitle"))
    category = clean((store.get("category") or {}).get("title"))
    record = {
        "club": CLUB_NAME,
        "business_name": name,
        "discount": " - ".join(part for part in (title, subtitle) if part),
        "discount_url": deals_url(mall["slug"]),
        "discount_type": "voucher",
        "discount_value": saving_percent(title),
        "has_physical_store": True,
        "branches": [{"mall": mall["name"]}],
        "limitations": html_to_text(details.get("finePrints") or ""),
        "_deal_id": deal.get("id"),
    }
    if category:
        record["category"] = category
    return record


def parse_deals_page(html: str, mall: dict[str, str]) -> tuple[list[dict[str, Any]], int]:
    props = page_props(html)
    records = [deal_to_record(deal, mall) for deal in props.get("deals") or [] if isinstance(deal, dict)]
    total = props.get("numberOfItems") or 0
    return [r for r in records if r], int(total) if str(total).isdigit() else 0


def merge_by_deal(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[Any, dict[str, Any]] = {}
    order = []
    for record in records:
        key = record.get("_deal_id") or (record["business_name"], record["discount"])
        if key not in merged:
            merged[key] = record
            order.append(key)
        else:
            known = {b["mall"] for b in merged[key]["branches"]}
            merged[key]["branches"].extend(b for b in record["branches"] if b["mall"] not in known)
    result = []
    for key in order:
        record = merged[key]
        record.pop("_deal_id", None)
        malls = [b["mall"] for b in record["branches"]]
        if len(malls) > 1:
            record["discount_url"] = BASE_URL
        result.append(record)
    return dedupe(result)


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for mall in parse_malls(fetch(BASE_URL)):
        try:
            first, total = parse_deals_page(fetch(deals_url(mall["slug"])), mall)
        except Exception as exc:
            print(f"WARNING: {mall['slug']} deals failed: {exc}")
            continue
        records.extend(first)
        pages = min(MAX_PAGES, math.ceil(total / PAGE_SIZE)) if total else 1
        for page in range(2, pages + 1):
            try:
                more, _ = parse_deals_page(fetch(deals_url(mall["slug"], page)), mall)
            except Exception as exc:
                print(f"WARNING: {mall['slug']} page {page} failed: {exc}")
                continue
            if not more:
                break
            records.extend(more)
    return merge_by_deal(records)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {"home.html": fetch(BASE_URL)}


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} deals")
    for item in items[:3]:
        print(item)
