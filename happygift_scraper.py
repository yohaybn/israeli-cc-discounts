"""Scraper for businesses that accept the HappyGift gift cards (קשרים פלוס).

COVERAGE.md had +HappyGift marked blocked because the storefront (plus.happygift.co.il) is an
Angular app. The public catalog site (catalog.happygift.co.il, no login) is a Next.js app whose
server-rendered React Server Components payload already embeds the full "where to use" list for
each card under "suppliers", with branches in separate text chunks. No browser is needed.

Cards covered:
* +HappyGift          - coupon 5041
* HappyGift Multi     - coupons 3198 (physical) and 4313 (digital), merged
"""

import json
import re
from typing import Any, Callable

from scraper_utils import clean, dedupe, fetch_text, html_to_text

SOURCE_KEY = "happygift"
CLUB_NAME = "HappyGift"
BASE_URL = "https://catalog.happygift.co.il/coupon-suppliers/"
# club name -> catalog coupon ids
CARDS = {
    "+HappyGift": ["5041"],
    "HappyGift Multi": ["3198", "4313"],
}
ONLINE_ADDRESS = "אתר אונליין"
NATIONWIDE_ADDRESS = "פריסה ארצית"
PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
PG_ITEM_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def rsc_payload(html: str) -> str:
    """Join the Next.js flight chunks embedded in the page into one string."""
    return "".join(json.loads(chunk) for chunk in PUSH_RE.findall(html or ""))


def text_chunk(payload: str, ref: str) -> str:
    """Resolve a "$<id>" reference to its "<id>:T<hexlen>," text chunk (length is in UTF-8 bytes)."""
    match = re.search(r"(?<![0-9a-zA-Z])" + re.escape(ref) + r":T([0-9a-f]+),", payload)
    if not match:
        return ""
    size = int(match.group(1), 16)
    raw = payload[match.end():].encode("utf-8")[:size]
    return raw.decode("utf-8", errors="ignore")


def parse_pg_json_array(value: str) -> list[dict[str, Any]]:
    """Parse a Postgres array literal of JSON objects: {"{\\"id\\":1}","{...}"}."""
    items = []
    for element in PG_ITEM_RE.findall(value or ""):
        try:
            item = json.loads(json.loads(f'"{element}"'))
        except ValueError:
            continue
        if isinstance(item, dict):
            items.append(item)
    return items


def extract_suppliers(html: str) -> list[dict[str, Any]]:
    payload = rsc_payload(html)
    marker = '"suppliers":'
    start = payload.find(marker)
    if start < 0:
        return []
    try:
        suppliers, _ = json.JSONDecoder().raw_decode(payload[start + len(marker):])
    except ValueError:
        return []
    result = []
    for supplier in suppliers if isinstance(suppliers, list) else []:
        if not isinstance(supplier, dict):
            continue
        branches_raw = supplier.get("supplierBranches") or ""
        if isinstance(branches_raw, str) and branches_raw.startswith("$"):
            branches_raw = text_chunk(payload, branches_raw[1:])
        supplier = dict(supplier)
        supplier["_branches"] = parse_pg_json_array(branches_raw) if isinstance(branches_raw, str) else []
        result.append(supplier)
    return result


def supplier_to_record(supplier: dict[str, Any], card: str, coupon_id: str) -> dict[str, Any] | None:
    name = clean(supplier.get("name") or supplier.get("companyName"))
    if not name:
        return None
    address = clean(supplier.get("address"))
    branches = []
    for branch in supplier.get("_branches") or []:
        entry = {"name": clean(branch.get("name")), "address": clean(branch.get("address")), "phone": clean(branch.get("phone"))}
        entry = {k: v for k, v in entry.items() if v}
        if entry.get("address") or entry.get("name"):
            branches.append(entry)
    if not branches and address and address not in (ONLINE_ADDRESS, NATIONWIDE_ADDRESS):
        branches.append({"address": address})
    short = clean(supplier.get("shortdescription") or supplier.get("shortDescription"))
    details = html_to_text(supplier.get("description") or "")
    record = {
        "club": card,
        "business_name": name,
        "discount": short or f"מכבד את כרטיס המתנה {card}",
        "discount_url": f"{BASE_URL}{coupon_id}",
        "discount_type": "gift_card",
        "discount_value": None,
        "has_physical_store": address != ONLINE_ADDRESS,
        "branches": branches,
        "limitations": details,
    }
    category = clean(supplier.get("secondary_category_name") or supplier.get("main_category_name"))
    if category:
        record["category"] = category
    return record


def parse_page(html: str, card: str, coupon_id: str) -> list[dict[str, Any]]:
    records = [supplier_to_record(s, card, coupon_id) for s in extract_suppliers(html)]
    return [r for r in records if r]


def merge_card(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge the same business listed under several coupon ids of one card (physical + digital)."""
    merged: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record["business_name"].strip().lower()
        if key in merged:
            existing = merged[key]
            known = {json.dumps(b, sort_keys=True, ensure_ascii=False) for b in existing["branches"]}
            for branch in record["branches"]:
                if json.dumps(branch, sort_keys=True, ensure_ascii=False) not in known:
                    existing["branches"].append(branch)
        else:
            merged[key] = record
    return list(merged.values())


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    out = []
    for card, coupon_ids in CARDS.items():
        records = []
        for coupon_id in coupon_ids:
            try:
                html = fetch(f"{BASE_URL}{coupon_id}")
            except Exception as exc:  # one failing coupon page must not drop the others
                print(f"[WARNING] HappyGift coupon {coupon_id} failed: {exc}")
                continue
            records.extend(parse_page(html, card, coupon_id))
        out.extend(merge_card(records))
    return dedupe(out)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    return {f"coupon_{cid}.html": fetch(f"{BASE_URL}{cid}") for ids in CARDS.values() for cid in ids}


if __name__ == "__main__":
    items = scrape()
    print(f"{len(items)} HappyGift records")
    for card in CARDS:
        print(card, sum(1 for i in items if i["club"] == card))
