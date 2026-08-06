import json
import re
import time
from bs4 import BeautifulSoup
import requests

MCC_URL = "https://www.mcc.co.il/st_reshet_public.aspx"
BASE_DISCOUNT_URL = "https://www.mcc.co.il/site/pg/st_reshet_out&p1="

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/x-www-form-urlencoded",
}


def scrape_mcc():
    print("--- Starting MCC Scraper ---")
    session = requests.Session()
    response = session.get(MCC_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Map Main Categories
    main_categories = {}
    select_main = soup.select_one("select#Select1")
    if select_main:
        for option in select_main.find_all("option"):
            val = option.get("value")
            if val and val != "0":
                main_categories[val] = option.get_text(strip=True)

    # Parse Subcategories JS Array
    js_match = re.search(
        r"var new_types = new Array\s*\((.*?)\);", response.text, re.DOTALL
    )

    sub_categories = []
    if js_match:
        raw_tuples = re.findall(
            r"new Array\((\d+),(\d+),'([^']+)'\)", js_match.group(1)
        )
        for main_id, sub_id, _ in raw_tuples:
            sub_categories.append({"main_id": main_id, "sub_id": sub_id})

    results = []
    seen_combinations = set()

    print(f"[MCC] Processing {len(sub_categories)} subcategories...")

    for idx, cat in enumerate(sub_categories, 1):
        payload = {
            "is_searching": "0",
            "region": "0",
            "second_type": cat["sub_id"],
            "txtSearch": "",
            "cmb_main_type": cat["main_id"],
            "cmb_second_type_i": cat["sub_id"],
            "cmb_region2": "0",
            "mode": "",
            "search_method": "type",
            "main_type": cat["main_id"],
            "second_type_i": cat["sub_id"],
            "region2": "0",
        }

        try:
            res = session.post(MCC_URL, data=payload, headers=HEADERS)
            page_soup = BeautifulSoup(res.text, "html.parser")
            rows = page_soup.select("#object_table tbody tr")

            for row in rows:
                title_elem = row.select_one(".title")
                discount_elem = row.select_one("h2")
                img_elem = row.select_one("img.logo")

                if not title_elem:
                    continue

                business_name = title_elem.get_text(strip=True)
                discount = (
                    discount_elem.get_text(strip=True) if discount_elem else ""
                )

                # Deduplicate identical business + discount entries across categories
                dedup_key = f"{business_name}_{discount}"
                if dedup_key in seen_combinations:
                    continue
                seen_combinations.add(dedup_key)

                onclick_attr = row.get("onclick", "")
                id_match = re.search(r"mclick\((\d+)\)", onclick_attr)
                discount_url = (
                    f"{BASE_DISCOUNT_URL}{id_match.group(1)}"
                    if id_match
                    else ""
                )

                logo = ""
                if img_elem:
                    logo_src = img_elem.get("data-src") or img_elem.get("src")
                    if logo_src and not logo_src.startswith("http"):
                        logo = f"https://www.mcc.co.il/{logo_src.lstrip('/')}"
                    else:
                        logo = logo_src or ""

                results.append({
                    "club": "MCC",
                    "business_name": business_name,
                    "discount": discount,
                    "logo_url": logo,
                    "discount_url": discount_url,
                })

            print(
                f"[MCC {idx}/{len(sub_categories)}] Extracting... Total items"
                f" so far: {len(results)}"
            )
        except Exception as e:
            print(f"MCC Error: {e}")

        time.sleep(0.2)

    return results


if __name__ == "__main__":
    import os
    data = scrape_mcc()
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "mcc_discounts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} normalized items to {out_path}")