#!/usr/bin/env python3
"""Join discounts with geocoded physical store records.

Output:
 - docs/data/businesses_with_discounts.json
 - docs/data/unmatched_discounts.json

Matching strategy:
 - Normalize names (lower, strip punctuation/diacritics)
 - For each discount, find geocoded store within 50 meters and with RapidFuzz
   token_set_ratio >= 80. If found, attach discount to that branch.
 - Otherwise record as unmatched for manual review.
"""
import json
import math
import os
import re
from typing import Any, Dict, List

try:
    from rapidfuzz.fuzz import token_set_ratio
except Exception:
    token_set_ratio = None
    # fallback implementation using difflib
    from difflib import SequenceMatcher


    def token_set_ratio(a: str, b: str) -> int:
        # simple approximation of RapidFuzz token_set_ratio
        if not a or not b:
            return 0
        ta = set(a.split())
        tb = set(b.split())
        # combine tokens with intersection prioritized
        common = ta & tb
        rest = (ta | tb) - common
        sa = " ".join(sorted(common))
        sb = " ".join(sorted(common))
        if rest:
            sa = sa + " " + " ".join(sorted(ta - common))
            sb = sb + " " + " ".join(sorted(tb - common))
        ratio = SequenceMatcher(None, sa, sb).ratio()
        return int(ratio * 100)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOCS_DATA = os.path.join(BASE_DIR, "docs", "data")
OUT_FILE = os.path.join(DOCS_DATA, "businesses_with_discounts.json")
UNMATCHED_FILE = os.path.join(DOCS_DATA, "unmatched_discounts.json")


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def normalize_name(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    # remove punctuation
    s = re.sub(r"[\W_]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def haversine_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    # returns distance in kilometers
    R = 6371.0088
    phi1 = math.radians(a_lat)
    phi2 = math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlambda = math.radians(b_lon - a_lon)
    x = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


def build_branches(geocoded: List[Dict]) -> List[Dict]:
    branches = []
    for i, s in enumerate(geocoded):
        lat = s.get("lat") or s.get("latitude") or s.get("lng") or s.get("lon")
        lon = s.get("lng") or s.get("lon") or s.get("longitude")
        try:
            lat = float(lat)
            lon = float(lon)
        except Exception:
            continue
        name = s.get("business_name") or s.get("name") or s.get("business") or ""
        branch = {
            "branch_id": f"g_{i}",
            "name": name,
            "name_norm": normalize_name(name),
            "lat": lat,
            "lng": lon,
            "discounts": [],
            "source_records": [s],
        }
        branches.append(branch)
    return branches


def build_token_index(branches: List[Dict]) -> Dict[str, List[int]]:
    idx: Dict[str, List[int]] = {}
    for i, br in enumerate(branches):
        tokens = set(br["name_norm"].split())
        for t in tokens:
            idx.setdefault(t, []).append(i)
    return idx


def match_and_join(discounts: List[Dict], branches: List[Dict],
                   max_dist_m: float = 50.0, name_threshold: int = 80) -> List[Dict]:
    unmatched = []
    # build token index for branches
    token_idx = build_token_index(branches)

    for disc in discounts:
        bname = disc.get("business_name") or disc.get("business") or disc.get("merchant") or ""
        addr = disc.get("address") or ""
        name_norm = normalize_name(bname + " " + addr)

        tokens = set(name_norm.split()) if name_norm else set()
        candidate_idxs = set()
        for t in tokens:
            for i in token_idx.get(t, []):
                candidate_idxs.add(i)

        # if no token overlap, fall back to all branches (expensive) but try to avoid
        if not candidate_idxs:
            candidate_idxs = set(range(len(branches)))

        best = None
        best_score = 0
        best_dist = None

        # determine if discount has coords
        disc_lat = disc.get("lat") or disc.get("latitude")
        disc_lng = disc.get("lng") or disc.get("lon")
        has_coords = False
        try:
            disc_lat = float(disc_lat)
            disc_lng = float(disc_lng)
            has_coords = True
        except Exception:
            has_coords = False

        for i in candidate_idxs:
            br = branches[i]
            # compute name similarity
            score = token_set_ratio(name_norm, br["name_norm"]) if name_norm and br["name_norm"] else 0

            if has_coords:
                dist_km = haversine_km(br["lat"], br["lng"], disc_lat, disc_lng)
                dist_m = dist_km * 1000
                if dist_m <= max_dist_m and score >= name_threshold:
                    if score > best_score or (score == best_score and (best_dist is None or dist_m < best_dist)):
                        best = br
                        best_score = score
                        best_dist = dist_m
            else:
                # no coordinates: allow match by name only
                if score >= name_threshold:
                    if score > best_score:
                        best = br
                        best_score = score
                        best_dist = None

        if best:
            d = dict(disc)
            d["matched_distance_m"] = best_dist
            best["discounts"].append(d)
        else:
            unmatched.append(disc)

    return unmatched


def compute_best_discount(branches: List[Dict]) -> None:
    for br in branches:
        best = None
        for d in br["discounts"]:
            try:
                val = float(d.get("discount_value") or d.get("value") or 0)
            except Exception:
                val = 0
            if best is None or val > best:
                best = val
        br["best_discount_value"] = best or 0


def main():
    all_disc_path = os.path.join(DOCS_DATA, "all_combined_discounts.json")
    geocoded_path = os.path.join(DOCS_DATA, "businesses", "processed_physical_stores_geocoded.json")

    print("Loading discounts...", all_disc_path)
    discounts = load_json(all_disc_path)
    print(f"Loaded {len(discounts)} discounts")

    print("Loading geocoded stores...", geocoded_path)
    geocoded = load_json(geocoded_path)
    print(f"Loaded {len(geocoded)} geocoded store records")

    branches = build_branches(geocoded)
    print(f"Built {len(branches)} branches from geocoded data")

    unmatched = match_and_join(discounts, branches, max_dist_m=50.0, name_threshold=80)
    print(f"Matched discounts; unmatched count: {len(unmatched)}")

    compute_best_discount(branches)

    # filter out branches without discounts
    branches_with_discounts = [b for b in branches if b["discounts"]]
    print(f"Branches with discounts: {len(branches_with_discounts)}")

    save_json(OUT_FILE, branches_with_discounts)
    save_json(UNMATCHED_FILE, unmatched)

    print(f"Wrote {OUT_FILE} and {UNMATCHED_FILE}")


if __name__ == "__main__":
    main()
