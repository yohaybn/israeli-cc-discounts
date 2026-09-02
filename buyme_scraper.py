#!/usr/bin/env python3
"""Simple scraper for Buyme vouchers (type: voucher).

Usage:
  python buyme_scraper.py --supplier 13438757

Outputs JSON to `data/buyme_<supplier_id>.json` with supplier info and list of stores (brands).
"""
import argparse
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import html
from urllib.parse import quote_plus

import requests

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fetch_options(supplier_id: int) -> Any:
    url = f"https://buyme.co.il/brands/{supplier_id}/options"
    headers = {"User-Agent": "discount-finder-bot/1.0 (+https://github.com)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_supplier_name(supplier_id: int) -> str:
    # Try the supplier page and extract a heading
    url = f"https://buyme.co.il/supplier/{supplier_id}"
    headers = {"User-Agent": "discount-finder-bot/1.0 (+https://github.com)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        text = resp.text
        if BeautifulSoup:
            soup = BeautifulSoup(text, "html.parser")
            # common heading tags
            for tag in ("h1", "h2", "h3"):
                el = soup.find(tag)
                if el and el.get_text(strip=True):
                    return el.get_text(strip=True)
        # fallback: regex to find <h1>..</h1>
        m = re.search(r"<h1[^>]*>([^<]+)</h1>", text)
        if m:
            return m.group(1).strip()
    except Exception:
        LOGGER.debug("Could not fetch supplier page", exc_info=True)
    return ""


def parse_brands(options: Any) -> List[Dict[str, Any]]:
    # options may be a dict with keys or a list
    brands = None
    if isinstance(options, dict):
        # common key name guess
        for key in ("brands", "items", "data", "suppliers"):
            if key in options and isinstance(options[key], (list, dict)):
                brands = options[key]
                break
        if brands is None:
            # maybe the dict itself represents a single brand
            # or a mapping of ids->brand
            # try to detect brand-like structure
            if any(k in options for k in ("title", "id", "siteAddress")):
                brands = [options]
    elif isinstance(options, list):
        brands = options

    if brands is None:
        return []

    stores = []
    for b in brands:
        try:
            store = {
                "id": b.get("id") or b.get("nid") or b.get("suppliers_id"),
                "title": b.get("title") or b.get("name"),
                "siteAddress": b.get("siteAddress"),
                "phone": b.get("phone"),
                "logo": b.get("logo") or b.get("main_pic"),
                "smallPrint": b.get("smallPrint"),
                "supplier_regions": [r.get("name") for r in (b.get("supplier_regions") or []) if isinstance(r, dict)],
            }
            stores.append(store)
        except Exception:
            LOGGER.debug("Error parsing brand entry", exc_info=True)
    return stores


def scrape_supplier(supplier_id: int) -> Dict[str, Any]:
    LOGGER.info("Fetching options for supplier %s", supplier_id)
    options = fetch_options(supplier_id)
    supplier_name = fetch_supplier_name(supplier_id)
    stores = parse_brands(options)

    supplier_info = {
        "id": supplier_id,
        "name": supplier_name,
    }

    # try to find a supplier-level blob in the options payload
    if isinstance(options, dict):
        for k in ("supplier", "merchant", "seller"):
            if k in options and isinstance(options[k], dict):
                supplier_info.update({
                    "logo": options[k].get("logo"),
                    "description": options[k].get("description") or options[k].get("name"),
                    "terms": options[k].get("terms") if "terms" in options[k] else None,
                })
                break

    return {"supplier": supplier_info, "stores": stores}


def stores_to_discounts(stores: List[Dict[str, Any]], supplier_name: str = None, supplier_ids_fallback: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Convert parsed buyme stores into normalized discount dicts.

    Fields produced (kept minimal):
      - club: 'BUYME'
      - business_name: store title
      - discount: smallPrint or 'Voucher'
      - discount_url: siteAddress if available
      - discount_type: 'voucher'
      - discount_value: None (attempt parse percent if present)
    """
    def clean_text(raw: Optional[str]) -> str:
        if not raw:
            return ""
        text = raw
        if BeautifulSoup:
            try:
                text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
            except Exception:
                text = raw
        else:
            # crude tag removal
            text = re.sub(r"<[^>]+>", " ", raw)
        text = html.unescape(text)
        # collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    out = []
    for s in stores:
        title = s.get("title") or s.get("business_name") or ""
        small_raw = s.get("smallPrint") or s.get("small_print") or ""
        small = clean_text(small_raw)
        site = s.get("siteAddress") or s.get("siteWeb") or ""

        # attempt to parse a percentage from cleaned small print
        dv = None
        try:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(%|אחוז)", small)
            if m:
                dv = float(m.group(1))
        except Exception:
            dv = None

        # supplier_name handling: stores may include supplier_names list
        s_names = s.get("supplier_names") or s.get("supplier_name") or supplier_name
        # normalize supplier_name: if list keep list, else keep string
        if isinstance(s_names, list):
            supplier_field = s_names if len(s_names) > 1 else (s_names[0] if s_names else None)
        else:
            supplier_field = s_names

        # build discount_url: prefer site; otherwise, build buyme search URL using supplier id and store name
        discount_url = site
        if not discount_url:
            # try to get a supplier id from store entry
            s_ids = s.get("supplier_ids") or s.get("supplier_id")
            if isinstance(s_ids, list) and len(s_ids) > 0:
                sid_for_url = s_ids[0]
            elif isinstance(s_ids, int) or (isinstance(s_ids, str) and s_ids.isdigit()):
                sid_for_url = int(s_ids)
            else:
                # fallback to provided supplier_ids_fallback
                sid_for_url = supplier_ids_fallback[0] if supplier_ids_fallback and len(supplier_ids_fallback) > 0 else None

            if sid_for_url:
                term = quote_plus(title)
                discount_url = f"https://buyme.co.il/brands/{sid_for_url}?searchTerm={term}#"

        item = {
            "club": "BUYME",
            "business_name": title,
            "discount": (f"{dv}%" if dv is not None else (small if small else "Voucher")),
            "discount_url": discount_url,
            "discount_type": "voucher",
            "discount_value": dv,
            "supplier_name": supplier_field,
        }
        out.append(item)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Buyme voucher scraper")
    p.add_argument("--supplier", required=True, help="Supplier id (or comma-separated ids)")
    args = p.parse_args()
    ids = [s.strip() for s in args.supplier.split(",") if s.strip()]
    for sid in ids:
        try:
            sid_int = int(sid)
        except ValueError:
            LOGGER.error("Invalid supplier id: %s", sid)
            continue
        out = scrape_supplier(sid_int)

        # Only normalize to the combined-discount format; do not persist raw supplier/store JSON.
        stores = out.get("stores") if isinstance(out, dict) else None
        supplier_name = out.get("supplier", {}).get("name") if isinstance(out, dict) else None
        if stores:
            discounts = stores_to_discounts(stores, supplier_name=supplier_name, supplier_ids_fallback=[sid_int])
            LOGGER.info("Converted %s BuyMe normalized discounts for supplier %s", len(discounts), sid_int)
            preview = discounts[:3]
            print(f"Preview of normalized discounts ({len(discounts)} total), first {len(preview)} entries:")
            print(json.dumps(preview, ensure_ascii=False, indent=2))


# Default supplier list used across the project
BUYME_SUPPLIERS = [
    13438757,
    9018727,
    752649,
    17573505,
    17573648,
    17573499,
    17573460,
    20620,
    15490363,
    17573615,
    17573670,
    15579925,
    17574524,
    15925581,
    17574048,
    4299680,
    17573995,
]


def scrape_buyme_suppliers(suppliers: Optional[List[int]] = None, out_dir: str = "data") -> Dict[str, Any]:
    """Scrape multiple BuyMe suppliers and deduplicate store records without writing raw JSON artifacts.

    Returns a dict with the normalized deduplicated store list and supplier counts.
    """
    if suppliers is None:
        suppliers = BUYME_SUPPLIERS

    buyme_index = {}
    buyme_counts = {}

    for sid in suppliers:
        try:
            bdata = scrape_supplier(sid)
        except Exception as e:
            LOGGER.warning("buyme scraper failed for %s: %s", sid, e)
            continue

        stores = bdata.get("stores") or []
        supplier_name = None
        if isinstance(bdata, dict):
            supplier_name = bdata.get("supplier", {}).get("name")
        buyme_counts[str(sid)] = len(stores)

        for s in stores:
            sid_key = s.get("id") or s.get("nid") or s.get("suppliers_id")
            if sid_key:
                key = f"id:{sid_key}"
            else:
                title = (s.get("title") or s.get("name") or "").strip().lower()
                key = f"title:{title}"

            if key in buyme_index:
                existing = buyme_index[key]
                snames = existing.get("supplier_names") or []
                if supplier_name and supplier_name not in snames:
                    snames.append(supplier_name)
                    existing["supplier_names"] = snames
                if not existing.get("siteAddress") and s.get("siteAddress"):
                    existing["siteAddress"] = s.get("siteAddress")
                if not existing.get("smallPrint") and s.get("smallPrint"):
                    existing["smallPrint"] = s.get("smallPrint")
                existing.setdefault("supplier_ids", [])
                if sid not in existing["supplier_ids"]:
                    existing["supplier_ids"].append(sid)
            else:
                entry = s.copy()
                entry["supplier_names"] = [supplier_name] if supplier_name else []
                entry["supplier_ids"] = [sid]
                buyme_index[key] = entry

    buyme_stores = list(buyme_index.values())

    return {
        "stores": buyme_stores,
        "supplier_counts": buyme_counts,
    }


if __name__ == "__main__":
    main()
