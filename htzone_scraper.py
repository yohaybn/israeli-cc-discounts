import json
import time
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests
except ImportError:
    import requests

URL = "https://www.htzone.co.il/_ajax/ajax.index.php"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.htzone.co.il",
    "referer": "https://www.htzone.co.il/sale/62",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}


def scrape_htzone(page_id=62, batch_size=50):
    print("--- Starting HTzone Scraper ---")
    results = []
    start = 0
    seen_ids = set()

    try:
        session = requests.Session(impersonate="chrome120")
    except Exception:
        session = requests.Session()

    while True:
        data = {
            "act": "get_sale_html",
            "start": str(start),
            "count": str(batch_size),
            "filter": "1",
            "page_id": str(page_id),
            "brand": "[]",
            "date": "[]",
            "area": "[]",
            "category": "[]",
            "file": "sale",
        }

        try:
            res = session.post(URL, headers=HEADERS, data=data, timeout=15)
            if res.status_code != 200:
                print(f"[HTzone] Stopping at start={start}. Status code: {res.status_code}")
                break

            res_json = res.json()
            html_content = res_json.get("sale_html", "")
        except Exception as e:
            print(f"[HTzone] Exception on start={start}: {e}")
            break

        if not html_content:
            print(f"[HTzone] No HTML content returned at start={start}.")
            break

        soup = BeautifulSoup(html_content, "html.parser")
        anchors = soup.find_all("a", class_="inherit")

        if not anchors:
            print(f"[HTzone] Reached end of items list at start={start}.")
            break

        new_count = 0
        for a_tag in anchors:
            item_id = a_tag.get("data-item") or a_tag.get("item_id") or ""
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            # Extract title: prefer div.item_text if available because single quotes in item_name HTML attribute (e.g. item_name='ג' פניקה ') can break HTML parsing of item_name
            text_div = a_tag.find("div", class_="item_text")
            if text_div and text_div.text.strip():
                title = text_div.text.strip().split('\n')[0]
            else:
                title = (a_tag.get("item_name") or "").strip()

            price = a_tag.get("item_price") or ""
            link = a_tag.get("href") or ""

            price_div = a_tag.find("div", class_="item_price")
            discount_text = (
                price_div.contents[0].strip()
                if price_div and price_div.contents
                else ""
            )

            discount_str = discount_text or (f"{price} ₪" if price else "הנחה לחברי מועדון")

            # Simple classification: default to billing_discount and extract percent when present
            discount_type = "billing_discount"
            discount_value = None
            pct_match = None
            try:
                pct_match = __import__('re').search(r"(\d+(?:\.\d+)?)\s*%", discount_str)
            except Exception:
                pct_match = None

            if pct_match:
                try:
                    discount_value = float(pct_match.group(1))
                except Exception:
                    discount_value = None

            results.append({
                "club": "HTzone",
                "business_name": title,
                "discount": discount_str,
                "discount_url": f"https://www.htzone.co.il{link}" if link and not link.startswith("http") else link,
                "discount_type": discount_type,
                "discount_value": discount_value,
                # HTzone: assume physical store by default
                "has_physical_store": True,
            })
            new_count += 1

        print(f"[HTzone] Batch start={start} (+{new_count} items) | Total accumulated: {len(results)}")

        if new_count == 0:
            break

        start += batch_size
        time.sleep(0.5)

    return results


if __name__ == "__main__":
    import os
    items = scrape_htzone()
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "htzone_discounts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(items)} items to {out_path}")