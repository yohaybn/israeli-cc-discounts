import json
import time
import requests

HOT_API_URL = "https://api.hot.co.il/api/website/2.0/getCategoryBenefits/?benefitType=100"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "origin": "https://www.hot.co.il",
    "priority": "u=1, i",
    "referrer": "https://www.hot.co.il/",
    "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

PAGE_SIZE = 100  # Pull 100 records per page to prevent HTTP 429 rate limits


def parse_hot_discount(item):
    """Normalize HOT discount strings from variable API fields."""
    value = item.get("value")
    small_text = item.get("small_text")
    before = item.get("price_before_discount")
    after = item.get("price_after_discount")

    if before and after:
        return f"{after} ₪ (במקום {before} ₪)"

    parts = []
    if value and value != "null":
        parts.append(str(value))
    if small_text:
        parts.append(str(small_text))

    return " ".join(parts).strip() if parts else "הנחה לחברי מועדון"


def scrape_hot():
    print("--- Starting HOT Club Scraper ---")
    results = []
    page = 1
    session = requests.Session()

    while True:
        payload = {
            "page": str(page),
            "size": str(PAGE_SIZE),
            "category": "688",
            "benefitType": "100",
            "sessionToken": "null",
        }

        # Handling rate limits (HTTP 429) gracefully
        retry_count = 0
        res = None
        while retry_count <= 3:
            try:
                res = session.post(HOT_API_URL, headers=HEADERS, data=payload)
                if res.status_code == 429:
                    retry_count += 1
                    sleep_sec = retry_count * 5
                    print(
                        f"[HOT] Rate limit (429) hit on page {page}. Sleeping"
                        f" {sleep_sec}s..."
                    )
                    time.sleep(sleep_sec)
                    continue
                break
            except Exception as e:
                print(f"[HOT] Exception on page {page}: {e}")
                break

        if not res or res.status_code != 200:
            print(
                f"[HOT] Stopping. Response status: {res.status_code if res else 'None'}"
            )
            break

        try:
            data = res.json()
        except Exception:
            break

        records = (
            data.get("data", {}).get("records", [])
            if isinstance(data, dict)
            else []
        )

        if not records:
            print(
                f"[HOT] Reached end of benefits list at page {page}."
            )
            break

        for item in records:
            if not isinstance(item, dict):
                continue

            b_id = item.get("id") or ""
            image_path = item.get("imagePath") or ""

            logo = (
                f"https://www.hot.co.il{image_path}"
                if image_path and not image_path.startswith("http")
                else image_path
            )

            results.append({
                "club": "HOT",
                "business_name": (
                    item.get("clean_title") or item.get("title") or ""
                ).strip(),
                "discount": parse_hot_discount(item),
                "logo_url": logo,
                "discount_url": f"https://www.hot.co.il/benefit/{b_id}"
                if b_id
                else "",
            })

        print(
            f"[HOT] Page {page} done ({len(records)} items) | Total accumulated:"
            f" {len(results)}"
        )
        page += 1
        time.sleep(0.8)

    return results


if __name__ == "__main__":
    import os
    data = scrape_hot()
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "hot_discounts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} normalized items to {out_path}")