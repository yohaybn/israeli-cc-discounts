"""Small helpers shared by the scrapers registered in extra_sources.py."""

import re
import time
from typing import Any

from bs4 import BeautifulSoup

try:
    from curl_cffi import requests

    REQUESTS_KWARGS = {"impersonate": "chrome"}
except ImportError:  # pragma: no cover - fallback when curl_cffi is missing
    import requests

    REQUESTS_KWARGS = {}

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
}

PERCENT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%")
ONLINE_ONLY_PATTERN = re.compile(r"אונליין|באתר|online", re.IGNORECASE)
PHYSICAL_PATTERN = re.compile(r"בסניפ|בחנויות|בחנות|ברשת|בקופות")


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\u00a0", " ")).strip()


def html_to_text(value: Any) -> str:
    if not value:
        return ""
    return clean(BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True))


def percent_value(text: str) -> float | None:
    match = PERCENT_PATTERN.search(text or "")
    return float(match.group(1)) if match else None


def is_online_only(*texts: str) -> bool:
    joined = " ".join(t or "" for t in texts)
    return bool(ONLINE_ONLY_PATTERN.search(joined)) and not PHYSICAL_PATTERN.search(joined)


def fetch_text(url: str, timeout: int = 30, retries: int = 2, **kwargs) -> str:
    """GET a page, retrying transient connection errors (not HTTP errors) with a short backoff."""
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout, **REQUESTS_KWARGS, **kwargs)
        except Exception:
            if attempt == retries:
                raise
            time.sleep(2 * (attempt + 1))
            continue
        response.raise_for_status()
        return response.text
    raise RuntimeError("unreachable")


def dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for record in records:
        key = (record.get("business_name", "").lower(), record.get("discount", ""), record.get("discount_url", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return result
