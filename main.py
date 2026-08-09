from datetime import datetime, timezone
import json
import os
from hot_scraper import scrape_hot
from htzone_scraper import scrape_htzone
from mcc_scraper import scrape_mcc

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_existing_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
                elif isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[Warning] Could not load fallback JSON from {filepath}: {e}")
    return None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("================ STARTING CARDS COMPARISON SCRAPER ================\n")

    mcc_path = os.path.join(DATA_DIR, "mcc_discounts.json")
    hot_path = os.path.join(DATA_DIR, "hot_discounts.json")
    htzone_path = os.path.join(DATA_DIR, "htzone_discounts.json")
    combined_path = os.path.join(DATA_DIR, "all_combined_discounts.json")
    metadata_path = os.path.join(DATA_DIR, "scrape_metadata.json")

    # Load existing metadata if available
    metadata = load_existing_json(metadata_path)
    if not isinstance(metadata, dict):
        metadata = {}

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Scrape MCC
    mcc_data = scrape_mcc()
    if mcc_data and len(mcc_data) > 0:
        with open(mcc_path, "w", encoding="utf-8") as f:
            json.dump(mcc_data, f, ensure_ascii=False, indent=4)
        metadata["mcc"] = {
            "last_successful_scrape": now_iso,
            "count": len(mcc_data),
        }
        print(f"--> Saved {len(mcc_data)} normalized MCC items to {mcc_path}.\n")
    else:
        print(
            f"[WARNING] MCC Scraper returned 0 items. Retaining previous data"
            f" from {mcc_path}.\n"
        )
        mcc_data = load_existing_json(mcc_path) or []

    # 2. Scrape HOT
    hot_data = scrape_hot()
    if hot_data and len(hot_data) > 0:
        with open(hot_path, "w", encoding="utf-8") as f:
            json.dump(hot_data, f, ensure_ascii=False, indent=4)
        metadata["hot"] = {
            "last_successful_scrape": now_iso,
            "count": len(hot_data),
        }
        print(f"--> Saved {len(hot_data)} normalized HOT items to {hot_path}.\n")
    else:
        print(
            f"[WARNING] HOT Scraper returned 0 items. Retaining previous data"
            f" from {hot_path}.\n"
        )
        hot_data = load_existing_json(hot_path) or []

    # 3. Scrape HTzone
    htzone_data = scrape_htzone()
    if htzone_data and len(htzone_data) > 0:
        with open(htzone_path, "w", encoding="utf-8") as f:
            json.dump(htzone_data, f, ensure_ascii=False, indent=4)
        metadata["htzone"] = {
            "last_successful_scrape": now_iso,
            "count": len(htzone_data),
        }
        print(
            f"--> Saved {len(htzone_data)} normalized HTzone items to"
            f" {htzone_path}.\n"
        )
    else:
        print(
            f"[WARNING] HTzone Scraper returned 0 items. Retaining previous"
            f" data from {htzone_path}.\n"
        )
        htzone_data = load_existing_json(htzone_path) or []

    # 4. Create Combined Card Comparison File
    combined_list = mcc_data + hot_data + htzone_data
    if combined_list:
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(combined_list, f, ensure_ascii=False, indent=4)
        metadata["all_combined"] = {
            "last_updated": now_iso,
            "total_count": len(combined_list),
        }
        print(
            f"--> Updated combined file {combined_path} with"
            f" {len(combined_list)} total records."
        )

    # 5. Save Metadata File
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    print(f"--> Updated scrape metadata in {metadata_path}.")

    print("\n================ FINISHED PROCESS ================")
    print(
        f"Total normalized records in combined dataset: {len(combined_list)}"
    )


if __name__ == "__main__":
    main()