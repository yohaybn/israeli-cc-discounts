import json
import os
import requests
import sys

DATA_FILE = "docs/data/all_combined_discounts.json"
BUYME_FILE = "docs/data/buyme_discounts.json"
HVR_FILE = "docs/data/hvr_rechargeable_cards.json"
API_BASE = "http://127.0.0.1:8000"


def check_no_raw_buyme_artifacts():
    buyme_raw_dir = "docs/data/buyme"
    buyme_index_file = "docs/data/buyme_all_stores.json"
    if os.path.isdir(buyme_raw_dir):
        print(f"Raw BuyMe directory should not exist: {buyme_raw_dir}", file=sys.stderr)
        return 4
    if os.path.exists(buyme_index_file):
        print(f"Raw BuyMe index file should not exist: {buyme_index_file}", file=sys.stderr)
        return 5
    print("No raw BuyMe artifacts found on disk.")
    return 0


def check_data_file():
    for path in (DATA_FILE, BUYME_FILE, HVR_FILE):
        if not os.path.exists(path):
            print(f"Missing expected scraper output: {path}", file=sys.stderr)
            return 1
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"File is not a list: {path}", file=sys.stderr)
            return 1

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    missing_type = sum(1 for d in data if not d.get("discount_type"))
    print(f"Total records: {len(data)}, missing discount_type: {missing_type}")
    if missing_type > 0:
        print("Some records are missing discount_type - expected backfill to billing_discount", file=sys.stderr)
        return 2
    rechargeable = sum(1 for d in data if (d.get("discount_type") or "") == "rechargeable_card")
    print(f"Rechargeable card records: {rechargeable}")
    return 0


def check_api_endpoints():
    try:
        r = requests.get(API_BASE + "/api", timeout=5)
        r.raise_for_status()
        print("/api OK")

        r = requests.get(API_BASE + "/clubs", timeout=5)
        r.raise_for_status()
        print("/clubs OK")

        # sample filter
        r = requests.get(API_BASE + "/discounts", params={"discount_type": "billing_discount"}, timeout=10)
        r.raise_for_status()
        js = r.json()
        print(f"/discounts?discount_type=billing_discount returned {js.get('total')} results")
    except Exception as e:
        print(f"API check failed: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == '__main__':
    rc = check_no_raw_buyme_artifacts()
    if rc != 0:
        sys.exit(rc)
    rc = check_data_file()
    if rc != 0:
        sys.exit(rc)
    rc = check_api_endpoints()
    sys.exit(rc)
