"""Scraper for the store list of the Gifta (גיפטא) gift card, read from the public WordPress API."""

from typing import Any, Callable

from scraper_utils import dedupe, fetch_text
from wp_catalog import fetch_wp_collection, rendered, term_names

SOURCE_KEY = "gifta"
CLUB_NAME = "גיפטא"
BASE_URL = "https://gifta.co.il"
LIST_URL = "https://gifta.co.il/%D7%A8%D7%A9%D7%AA%D7%95%D7%AA-%D7%9E%D7%9B%D7%91%D7%93%D7%95%D7%AA/"
POST_FIELDS = "id,title,link,categories,excerpt"
# Categories that describe the site itself rather than a store type.
SKIP_CATEGORIES = {"Blog", "Uncategorized", "נקודות רכישה"}


def normalize_gifta(posts: list[dict[str, Any]], categories: dict[int, str]) -> list[dict[str, Any]]:
    records = []
    for post in posts:
        name = rendered(post, "title")
        if not name:
            continue
        cats = [categories.get(cid, "") for cid in post.get("categories") or []]
        cats = [c for c in cats if c and c not in SKIP_CATEGORIES and not c.startswith("רשימת")]
        cat_names = [categories.get(cid, "") for cid in post.get("categories") or []]
        if any(c in SKIP_CATEGORIES for c in cat_names) and not cats:
            continue
        addresses = " | ".join(part.strip() for part in rendered(post, "excerpt").split("📍") if part.strip())
        record = {
            "club": CLUB_NAME,
            "business_name": name,
            "discount": "מכבד את כרטיס המתנה גיפטא",
            "discount_url": post.get("link") or LIST_URL,
            "discount_type": "gift_card",
            "discount_value": None,
            "has_physical_store": True,
            "branches": [],
            "limitations": f"סניפים: {addresses}" if addresses else "",
        }
        if cats:
            record["category"] = cats[0]
        records.append(record)
    return dedupe(records)


def fetch_raw(fetch: Callable[[str], str] = fetch_text) -> dict[str, str]:
    import json

    return {
        "posts.json": json.dumps(fetch_wp_collection(BASE_URL, "posts", POST_FIELDS, fetch), ensure_ascii=False),
        "categories.json": json.dumps(fetch_wp_collection(BASE_URL, "categories", "id,name", fetch), ensure_ascii=False),
    }


def scrape(fetch: Callable[[str], str] = fetch_text) -> list[dict[str, Any]]:
    posts = fetch_wp_collection(BASE_URL, "posts", POST_FIELDS, fetch)
    categories = term_names(fetch_wp_collection(BASE_URL, "categories", "id,name", fetch))
    return normalize_gifta(posts, categories)


if __name__ == "__main__":
    items = scrape()
    print(f"Extracted {len(items)} {CLUB_NAME} stores")
    for item in items[:5]:
        print(item)
