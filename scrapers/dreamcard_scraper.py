"""Scraper for the DREAM CARD VIP club (Fox group brands).

DREAM CARD VIP (the club's credit card) gives 15% cashback in every club brand
(https://www.dreamcard.co.il/dreamcard-vip/). The club's web app exposes two public API
calls that need no login: Brands/GetBrands (the club brands) and Branches/GetBranchesData
(shopping complexes and the club stores inside them). This module emits one record per
active brand with its branches.
"""

import json
import re
from typing import Any, Callable

from scraper_utils import clean, dedupe

try:
    from curl_cffi import requests
except ImportError:  # pragma: no cover
    import requests

SOURCE_KEY = "dreamcard"
CLUB_NAME = "DREAM CARD VIP"
API_URL = "https://online.dreamcard.co.il/FoxDreamCardApiFront/api/"
INFO_URL = "https://www.dreamcard.co.il/dreamcard-vip/"
DISCOUNT_TEXT = "15% קאשבק בכל מותגי המועדון בכרטיס DREAM CARD VIP"
DISCOUNT_VALUE = 15
LIMITATIONS = "קאשבק נצבר לשימוש במותגי המועדון. בכרטיס מועדון רגיל (לא אשראי) הקאשבק הוא 10%. בכפוף לתקנון המועדון."
ALIASES = {"QUICKSILVER": "QUIKSILVER"}


def post_json(endpoint: str) -> dict[str, Any]:
    response = requests.post(
        API_URL + endpoint,
        json={},
        timeout=40,
        headers={"Origin": "https://online.dreamcard.co.il", "Referer": "https://online.dreamcard.co.il/public/branches"},
        **({"impersonate": "chrome"} if "curl_cffi" in requests.__name__ else {}),
    )
    response.raise_for_status()
    return response.json()


def _norm(name: str) -> str:
    name = ALIASES.get(clean(name).upper(), clean(name).upper())
    return re.sub(r"[^A-Z0-9]", "", name)


def stores_by_chain(branches_payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for complex_ in (branches_payload.get("data") or {}).get("complexesList") or []:
        for store in complex_.get("storeList") or []:
            if store.get("isActiveStore") is False:
                continue
            branch = {
                "name": clean(complex_.get("canyonName")) or clean(store.get("storeName")),
                "address": clean(complex_.get("complexStreet")),
                "city": clean(complex_.get("city")),
            }
            if clean(store.get("phoneNumber")):
                branch["phone"] = clean(store.get("phoneNumber"))
            if store.get("outletStore"):
                branch["outlet"] = True
            for part in str(store.get("chainName") or "").split("/"):
                key = _norm(part)
                if key and branch not in result.setdefault(key, []):
                    result[key].append(branch)
    return result


def build_records(brands_payload: dict[str, Any], branches_payload: dict[str, Any]) -> list[dict[str, Any]]:
    stores = stores_by_chain(branches_payload)
    records = []
    for brand in (brands_payload.get("data") or {}).get("lstBrands") or []:
        if brand.get("isActive") is False:
            continue
        english = clean(brand.get("brandName"))
        hebrew = clean(brand.get("brandNameHeb"))
        name = hebrew or english
        if not name:
            continue
        branches = stores.get(_norm(english), [])
        records.append({
            "club": CLUB_NAME,
            "business_name": f"{hebrew} ({english})" if hebrew and english else name,
            "discount": DISCOUNT_TEXT,
            "discount_url": clean(brand.get("siteUrl")) or INFO_URL,
            "discount_type": "club_card",
            "discount_value": DISCOUNT_VALUE,
            "has_physical_store": bool(branches),
            "branches": branches,
            "limitations": LIMITATIONS,
        })
    return dedupe(records)


def fetch_raw(post: Callable[[str], dict] = post_json) -> dict[str, str]:
    return {
        "brands.json": json.dumps(post("Brands/GetBrands"), ensure_ascii=False),
        "branches.json": json.dumps(post("Branches/GetBranchesData"), ensure_ascii=False),
    }


def scrape(post: Callable[[str], dict] = post_json) -> list[dict[str, Any]]:
    return build_records(post("Brands/GetBrands"), post("Branches/GetBranchesData"))


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} brands")
    for item in items[:3]:
        print({**item, "branches": item["branches"][:2]})
