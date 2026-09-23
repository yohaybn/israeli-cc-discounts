"""Shared client for club sites built on the uniq-club platform (admin.uniq-club.co.il).

uniq (https://www.uniq-club.co.il/, shop 1) and the Tel Aviv University club
(https://www.tauclub.co.il/, shop 2) are Angular apps that read their benefits from a public
GraphQL endpoint. The ``getBenefits`` query with ``{"shopId": N, "take": 1000}`` returns every
benefit of the shop (name, HTML description, a short ``discount`` line). No login is needed.
"""

import json
from typing import Any, Callable

from scraper_utils import clean, dedupe, html_to_text, is_online_only, percent_value

GRAPHQL_URL = "https://admin.uniq-club.co.il/api/graphql"
QUERY = (
    "query($f:FilterBenefitsInput){ getBenefits(filterBenefitsInput:$f){ count "
    "items { id name description discount discountCondition } } }"
)

Post = Callable[[str, dict], Any]


def request_body(shop_id: str) -> dict:
    return {"query": QUERY, "variables": {"f": {"shopId": str(shop_id), "take": 1000}}}


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


def default_post(url: str, body: dict) -> Any:
    try:
        from curl_cffi import requests as http
        response = http.post(url, json=body, impersonate="chrome", timeout=30)
    except ImportError:  # pragma: no cover
        import requests as http
        response = http.post(url, json=body, timeout=30)
    response.raise_for_status()
    return response.json()
