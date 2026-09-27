"""Shared client for club sites built on the uniq-club platform (admin.uniq-club.co.il).

uniq (https://www.uniq-club.co.il/, shop 1) and the Tel Aviv University club
(https://www.tauclub.co.il/, shop 2) are Angular apps that read their benefits from a public
GraphQL endpoint. The ``getBenefits`` query with ``{"shopId": N, "take": 1000}`` returns every
benefit of the shop (name, HTML description, a short ``discount`` line). The paginated
``products`` query adds only `type=coupon` items, not ordinary shop goods. No login is needed.
"""

import json
from datetime import datetime, timezone
from typing import Any, Callable

from scraper_utils import clean, dedupe, html_to_text, is_online_only, percent_value

GRAPHQL_URL = "https://admin.uniq-club.co.il/api/graphql"
BENEFIT_QUERY = (
    "query($f:FilterBenefitsInput){ getBenefits(filterBenefitsInput:$f){ count "
    "items { id name description discount discountCondition } } }"
)

PRODUCT_QUERY = (
    "query($filter:FilterProductInput!){products(filter:$filter){count items{"
    "id name type description price originalPrice unitsInStock isFree "
    "validFrom validUntil isNoRemainingCoupons(shopId:SHOP_ID) "
    "priceTextWhenFreeProduct isHideOriginalPrice}}}"
)
PRODUCT_PAGE_SIZE = 200
MAX_PRODUCT_PAGES = 30

Post = Callable[[str, dict], Any]


def request_body(shop_id: str) -> dict:
    return {"query": BENEFIT_QUERY, "variables": {"f": {"shopId": str(shop_id), "take": 1000}}}


def parse(payload: Any, club: str, site_url: str, limitations: str = "") -> list[dict[str, Any]]:
    if isinstance(payload, str):
        payload = json.loads(payload)
    items = (((payload or {}).get("data") or {}).get("getBenefits") or {}).get("items") or []
    records = []
    for item in items:
        name = clean(item.get("name"))
        if not name:
            continue
        description = html_to_text(item.get("description"))
        discount = clean(item.get("discount")) or clean(item.get("discountCondition"))
        text = discount or description[:200] or name
        limit_parts = [p for p in (limitations, clean(item.get("discountCondition"))) if p]
        records.append({
            "club": club,
            "business_name": name,
            "discount": text,
            "discount_url": site_url,
            "discount_type": "billing_discount",
            "discount_value": percent_value(discount) or percent_value(description),
            "has_physical_store": not is_online_only(text, description),
            "branches": [],
            "limitations": "; ".join(limit_parts),
        })
    return dedupe(records)


def fetch_benefits(shop_id: str, post: Post | None = None) -> Any:
    if post is None:
        post = default_post
    return post(GRAPHQL_URL, request_body(shop_id))


def product_request_body(shop_id: str, page: int) -> dict:
    return {
        "query": PRODUCT_QUERY.replace("SHOP_ID", json.dumps(str(shop_id))),
        "variables": {"filter": {"shopId": str(shop_id), "page": page, "take": PRODUCT_PAGE_SIZE}},
    }


def fetch_products(shop_id: str, post: Post | None = None) -> list[dict[str, Any]]:
    """Walk the public catalog; the API caps a page at 200 even with a larger take."""
    post = post or default_post
    products: list[dict[str, Any]] = []
    for page in range(MAX_PRODUCT_PAGES):
        result = post(GRAPHQL_URL, product_request_body(shop_id, page))
        if isinstance(result, str):
            result = json.loads(result)
        if result.get("errors"):
            raise ValueError(f"uniq products query failed on page {page}: {result['errors']}")
        catalog = ((result.get("data") or {}).get("products") or {})
        batch = catalog.get("items") or []
        products.extend(batch)
        count = catalog.get("count")
        if count is None:
            raise ValueError("uniq products catalog did not provide a total count")
        if len(products) >= int(count):
            break
        if not batch or len(batch) < PRODUCT_PAGE_SIZE:
            raise ValueError(f"uniq products catalog ended early: {len(products)} of {count}")
    else:
        raise ValueError("uniq products catalog exceeded safe page limit")
    ids = [str(item.get("id")) for item in products]
    if len(set(ids)) != len(ids) or len(products) != int(count):
        raise ValueError("uniq products catalog returned duplicate or incomplete pages")
    return products


def parse_coupons(products: list[dict[str, Any]], club: str, site_url: str,
                  limitations: str = "", now: datetime | None = None) -> list[dict[str, Any]]:
    """Only actual coupon products, not ordinary merchandise or QR checkout products."""
    now = now or datetime.now(timezone.utc)
    records = []
    for item in products:
        if str(item.get("type") or "").lower() != "coupon":
            continue
        name, ident = clean(item.get("name")), clean(item.get("id"))
        if not name or not ident or item.get("isNoRemainingCoupons") is True:
            continue
        try:
            if item.get("unitsInStock") is not None and float(item["unitsInStock"]) <= 0:
                continue
            price = float(item.get("price") or 0)
            original = float(item.get("originalPrice") or 0)
        except (ValueError, TypeError):
            continue
        valid_until = clean(item.get("validUntil"))
        if valid_until:
            try:
                expiry = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
                if expiry < now:
                    continue
            except ValueError:
                continue  # Unknown validity should not be advertised as current.
        description = html_to_text(item.get("description"))
        if not item.get("isFree") and price <= 0:
            continue
        text = (f"קופון ב-{price:g} ₪ במקום {original:g} ₪" if price and original > price
                else f"קופון ב-{price:g} ₪" if price else "קופון חינם")
        terms = "; ".join(x for x in (limitations, f"בתוקף עד {valid_until[:10]}" if valid_until else "") if x)
        records.append({
            "club": club, "business_name": name, "discount": text,
            "discount_url": site_url.rstrip("/") + "/product/" + ident,
            "discount_type": "coupon", "discount_value": None,
            "price": price, "original_price": original if original > 0 else None,
            "valid_until": valid_until or None, "voucher_type": "coupon",
            "has_physical_store": not is_online_only(name, description),
            "branches": [], "limitations": terms,
        })
    return dedupe(records)


def default_post(url: str, body: dict) -> Any:
    try:
        from curl_cffi import requests as http
        response = http.post(url, json=body, impersonate="chrome", timeout=30)
    except ImportError:  # pragma: no cover
        import requests as http
        response = http.post(url, json=body, timeout=30)
    response.raise_for_status()
    return response.json()
