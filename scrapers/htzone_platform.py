"""Shared crawler for club sites built on the HTzone white-label platform (*.htzone.co.il).

Clubs such as מצר (metzer.htzone.co.il) and גולד צפון (goldnorth.htzone.co.il) run on it.
The home page links category pages (``/category/N``). Each category page holds item blocks
(``data-act="category_items" data-target_id="M"``) whose items are loaded by a public POST to
``/ajax`` with ``act=category_items&id=M`` and the page token found in the page source.
Browsing is public; login is only needed to buy. The platform also sells shop products; those
are skipped and only merchant benefits and attraction vouchers are kept.
"""

import re
from typing import Any, Callable
from urllib.parse import urljoin

from scraper_utils import clean, dedupe, html_to_text, saving_percent

CATEGORY_RE = re.compile(r"""href=["'][^"']*?/category/(\d+)""")
BLOCK_RE = re.compile(r'data-act="category_items"\s+data-target_id="(\d+)"')
TOKEN_RE = re.compile(r"\btoken\s*=\s*'([0-9a-f]+)'")
TITLE_RE = re.compile(r"<title>\s*([^<]*?)\s*</title>", re.S)
# product_type 1 = shop products (furniture, appliances...) sold on the site; 2 = merchant
# benefits ("X% הנחה במעמד חיוב"), 4 = attractions/vouchers. Only 2 and 4 are club benefits.
BENEFIT_TYPES = {"2", "4"}

Fetch = Callable[[str], str]
Post = Callable[[str, dict], Any]


def category_ids(html: str) -> list[str]:
    return list(dict.fromkeys(CATEGORY_RE.findall(html or "")))


def block_ids(html: str) -> list[str]:
    return list(dict.fromkeys(BLOCK_RE.findall(html or "")))


def page_token(html: str) -> str:
    match = TOKEN_RE.search(html or "")
    return match.group(1) if match else ""


def category_name(html: str) -> str:
    match = TITLE_RE.search(html or "")
    title = clean(match.group(1)) if match else ""
    return clean(title.split("|", 1)[1]) if "|" in title else ""


def parse_items(payload: Any, base_url: str, club: str, category: str = "", limitations: str = "") -> list[dict[str, Any]]:
    items = payload.values() if isinstance(payload, dict) else (payload or [])
    records = []
    for item in items:
        if not isinstance(item, dict) or str(item.get("product_type")) not in BENEFIT_TYPES:
            continue
        title = clean(item.get("title_override") or item.get("title"))
        if not title:
            continue
        lead = item.get("lead_item") if isinstance(item.get("lead_item"), dict) else {}
        discount = clean(item.get("sub_title_override") or item.get("sub_title") or lead.get("sub_title"))
        corner = clean(lead.get("category_price_override") or item.get("price_override"))
        discount = discount or corner or title
        record = {
            "club": club,
            "business_name": title,
            "discount": discount,
            "discount_url": urljoin(base_url, f"/item/{item.get('id')}") if item.get("id") else base_url,
            "discount_type": "voucher",
            "discount_value": saving_percent(discount) or saving_percent(corner),
            "has_physical_store": True,
            "branches": [],
            "limitations": limitations,
        }
        if category:
            record["category"] = category
        records.append(record)
    return records


def crawl(base_url: str, club: str, fetch: Fetch, post: Post, limitations: str = "") -> list[dict[str, Any]]:
    home = fetch(base_url)
    records: list[dict[str, Any]] = []
    seen_blocks: set[str] = set()
    for cat_id in category_ids(home):
        try:
            html = fetch(urljoin(base_url, f"/category/{cat_id}"))
        except Exception as exc:  # one category should not sink the run
            print(f"WARNING: {base_url} category {cat_id} failed: {exc}")
            continue
        token, name = page_token(html), category_name(html)
        for block in block_ids(html):
            if block in seen_blocks:
                continue
            seen_blocks.add(block)
            try:
                payload = post(urljoin(base_url, "/ajax"), {"act": "category_items", "id": block, "sub_index": "", "token": token})
            except Exception as exc:
                print(f"WARNING: {base_url} block {block} failed: {exc}")
                continue
            records.extend(parse_items(payload, base_url, club, name, limitations))
    by_url: dict[str, dict[str, Any]] = {}
    for record in records:
        by_url.setdefault(record["discount_url"], record)
    return dedupe(list(by_url.values()))


def make_session_io():
    """fetch/post callables sharing one browser-like session (the ajax token is session-bound)."""
    try:
        from curl_cffi import requests as http
        session = http.Session(impersonate="chrome")
    except ImportError:  # pragma: no cover
        import requests as http
        session = http.Session()

    def fetch(url: str) -> str:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    def post(url: str, data: dict) -> Any:
        response = session.post(url, data=data, headers={"x-requested-with": "XMLHttpRequest"}, timeout=30)
        response.raise_for_status()
        return response.json()

    return fetch, post
