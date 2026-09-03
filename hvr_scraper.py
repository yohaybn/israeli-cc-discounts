import json
import os
import re
import time

try:
    from curl_cffi import requests
except ImportError:
    import requests
HEVER_DISCOUNT_VALUE=30
HVR_BASE = "https://www.hvr.co.il/bs2/datasets"
HVR_DATASETS = {
    "giftcard": {
        "url": f"{HVR_BASE}/giftcard.json",
        "label": "giftcard",
    },
    "teamimcard_branches": {
        "url": f"{HVR_BASE}/teamimcard_branches.json",
        "label": "teamimcard_branches",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.hvr.co.il/",
}


def normalize_hvr_rechargeable_card_item(item, source_name="giftcard"):
    """Map HVR gift-card/teamimcard source entries to the repo schema."""
    if not isinstance(item, dict):
        return None

    company = (
        item.get("company")
        or item.get("name")
        or item.get("merchant")
        or item.get("business_name")
        or ""
    ).strip()
    business_name = company or "כרטיס חבר"

    description_parts = []
    for key in [
        "company_desc",
        "desc",
        "category",
        "type",
        "search_words",
        "product_types",
    ]:
        value = item.get(key)
        if value and str(value).strip():
            description_parts.append(str(value).strip())

    city = item.get("city") or item.get("area") or ""
    address = item.get("address") or item.get("website") or ""
    limitations = item.get("limitations") or item.get("online_limitations") or ""

    discount_bits = []
    discount_bits.append("כרטיס חבר")

    if limitations and str(limitations).strip():
        discount_bits.append(str(limitations).strip())
    if description_parts:
        discount_bits.append(" | ".join(description_parts[:2]))

    discount = " | ".join(part for part in discount_bits if part).strip()
    if not discount:
        discount = "הטבת כרטיס חבר"

    website = item.get("website") or item.get("url") or item.get("site") or ""
    if website and not website.startswith("http"):
        website = "https://" + website if "." in website else website

    match = re.search(r"(\d+(?:\.\d+)?)\s*%", discount)
    discount_value = float(match.group(1)) if match else HEVER_DISCOUNT_VALUE

    return {
        "club": " חבר",
        "business_name": business_name,
        "discount": discount,
        "discount_url": website,
        "discount_type": "rechargeable_card",
        "discount_value": discount_value,
    }


def fetch_hvr_dataset(url):
    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            if response.status_code == 200:
                try:
                    payload = response.json()
                except ValueError:
                    body = response.content.lstrip(b"\xef\xbb\xbf")
                    payload = json.loads(body.decode("utf-8"))
                return payload
            if response.status_code == 429:
                print(f"[HVR] Rate-limited on attempt {attempt}. Sleeping {attempt * 5}s...")
                time.sleep(attempt * 5)
                continue
            print(f"[HVR] Unexpected status {response.status_code} for {url}")
            return []
        except Exception as exc:
            print(f"[HVR] Request failed for {url} on attempt {attempt}: {exc}")
            if attempt < 3:
                time.sleep(3)
    return []


def scrape_hvr_rechargeable_cards():
    print("--- Starting HVR Rechargeable Card Scraper ---")
    results = []

    for source_name, meta in HVR_DATASETS.items():
        payload = fetch_hvr_dataset(meta["url"])
        if not payload:
            print(f"[HVR] No data loaded for {source_name}.")
            continue

        items = []
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = payload.get("branch", []) if "branch" in payload else payload.get("items", [])
        elif isinstance(payload, tuple):
            items = list(payload)

        for item in items:
            normalized = normalize_hvr_rechargeable_card_item(item, source_name=source_name)
            if normalized:
                results.append(normalized)

        print(f"[HVR] {source_name}: {len(items)} raw items -> {len([x for x in items if True])} normalized")

    return results


if __name__ == "__main__":
    data = scrape_hvr_rechargeable_cards()
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "hvr_rechargeable_cards.json")
    if data:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(data)} normalized items to {out_path}")
    else:
        print("[ERROR] 0 items scraped for HVR rechargeable cards.")
