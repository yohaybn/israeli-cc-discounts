import json
import os
from hot_scraper import scrape_hot
from mcc_scraper import scrape_mcc

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("================ STARTING CARDS COMPARISON SCRAPER ================\n")

    # 1. Scrape MCC
    mcc_data = scrape_mcc()
    mcc_path = os.path.join(DATA_DIR, "mcc_discounts.json")
    with open(mcc_path, "w", encoding="utf-8") as f:
        json.dump(mcc_data, f, ensure_ascii=False, indent=4)
    print(f"--> Saved {len(mcc_data)} normalized MCC items to {mcc_path}.\n")

    # 2. Scrape HOT
    hot_data = scrape_hot()
    hot_path = os.path.join(DATA_DIR, "hot_discounts.json")
    with open(hot_path, "w", encoding="utf-8") as f:
        json.dump(hot_path, f, ensure_ascii=False, indent=4)
    print(f"--> Saved {len(hot_data)} normalized HOT items to {hot_path}.\n")

    # 3. Create Combined Card Comparison File
    combined_list = mcc_data + hot_data

    combined_path = os.path.join(DATA_DIR, "all_combined_discounts.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_list, f, ensure_ascii=False, indent=4)

    print("================ FINISHED PROCESS ================")
    print(
        f"Total normalized records extracted across both cards:"
        f" {len(combined_list)}"
    )


if __name__ == "__main__":
    main()