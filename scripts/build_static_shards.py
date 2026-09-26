#!/usr/bin/env python3
"""Publish compact static lookup files consumed by the Pages frontend.

Use deterministic names. The index is written last, after immutable content-hashed
shards, so a visitor with a cached index can continue to load its exact version.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import math
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs' / 'data'


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()[:12]


def shard_key(name):
    return hashlib.sha256(name.encode('utf-8')).hexdigest()[:2]


def canonical(label):
    s = label.strip().lower()
    aliases = {
        'mcc': 'mcc', 'חבר': 'mcc', 'חבר שלי': 'mcc-sheli', 'חבר טעמים': 'mcc-teamim',
        'hot': 'hot', 'מועדון הוט': 'hot', 'htzone': 'htzone', 'buyme': 'buyme',
        'max': 'max', 'giftcard max': 'max-giftcard', 'super giftcard max': 'max-super-giftcard',
        'giftcard food': 'max-food', 'כרטיס הטבות executive': 'max-executive',
        'מפתח דיסקונט': 'discount-key',
    }
    if s in aliases:
        return aliases[s]
    if 'BUYME' in label.upper():
        return 'buyme'
    slug = re.sub(r'[^a-z0-9\u0590-\u05ff]+', '-', unicodedata.normalize('NFKD', s)).strip('-')
    if slug:
        return 'program-' + slug
    h = 2166136261
    for char in (label or 'program'):
        h = ((h ^ ord(char)) * 16777619) & 0xffffffff
    return 'program-' + format(h, 'x')


def benefit_hash(club, name, discount):
    # Same FNV-1a / UTF-16 code units as docs/new_benefits.js.
    norm = lambda value: ' '.join(str(value or '').split()).lower()
    text = f'{club}|{norm(name)}|{norm(discount)}'
    h = 2166136261
    utf16 = text.encode('utf-16-le')
    for i in range(0, len(utf16), 2):
        h = ((h ^ int.from_bytes(utf16[i:i+2], 'little')) * 16777619) & 0xffffffff
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    out = ''
    while h:
        h, rem = divmod(h, 36)
        out = digits[rem] + out
    return out.rjust(7, '0')


def best_value(discounts):
    values = []
    for d in discounts:
        text = str(d.get('discount') or '')
        if str(d.get('discount_type') or '').lower() == 'voucher' or re.search(r'שובר|voucher|gift\s*card|גיפט|כרטיס\s*מתנה|שובר\s*מתנה', text, re.I):
            continue
        val = d.get('discount_value')
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
        else:
            m = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|אחוז(?:ים)?|percent)', text, re.I)
            if m:
                values.append(float(m.group(1)))
    return max(values, default=0)


def build_discounts():
    source = DOCS / 'all_combined_discounts.json'
    rows = json.loads(source.read_text(encoding='utf-8'))
    groups = defaultdict(list)
    counts = Counter()
    labels = set()
    for d in rows:
        name = str(d.get('business_name') or '').strip()
        label = str(d.get('club') or '').strip()
        if not name or not label:
            continue
        groups[name].append(d)
        counts[label] += 1
        labels.add(label)
    details = defaultdict(dict)
    index = []
    content_keys = defaultdict(dict)
    for name in sorted(groups):
        offers = groups[name]
        key = shard_key(name)
        clubs = sorted({d['club'] for d in offers})
        index.append({'business_name': name, 'clubs': clubs, 'discount_count': len(offers), 'club_counts': dict(Counter(d['club'] for d in offers)),
                      'best_discount_value': best_value(offers), 'shard': key,
                      'discount_types': sorted({str(d.get('discount_type') or '') for d in offers}),
                      'benefit_keys': []})
        details[key][name] = offers
        for d in offers:
            hash_value = benefit_hash(canonical(d['club']), name, d.get('discount'))
            content_keys[canonical(d['club'])][hash_value] = (name, key)
            index[-1]['benefit_keys'].append([d['club'], hash_value])
    output = DOCS / 'discount_shards'
    output.mkdir(exist_ok=True)
    manifest = {}
    for key, records in details.items():
        digest = save(output / f'{key}-pending.json', records)
        target = output / f'{key}-{digest}.json'
        (output / f'{key}-pending.json').replace(target)
        manifest[key] = f'{key}-{digest}.json'
    # Compact per-club hashes, compatible with NewBenefits' prior localStorage snapshot.
    catalog_version = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    hashes = {club: ''.join(sorted(records)) for club, records in content_keys.items()}
    hash_file = DOCS / f'benefit_hashes-{catalog_version}.json'
    save(hash_file, {'version': 1, 'catalog_version': catalog_version, 'clubs': hashes})
    save(DOCS / 'business_index.json', {'version': 1, 'catalog_version': catalog_version, 'labels': sorted(labels),
                                       'club_counts': counts, 'total': sum(counts.values()), 'benefit_hashes': hash_file.name,
                                       'businesses': index, 'shards': manifest})
    print(f'Built {len(index)} businesses, {len(rows)} benefits, {len(manifest)} detail shards')


def build_nearby():
    source = DOCS / 'businesses_with_discounts.json'
    rows = json.loads(source.read_text(encoding='utf-8'))
    # A 0.01-degree grid gives small (~2km) files, with the query fetching every
    # grid cell intersecting its bounding box. Coordinates are never rounded.
    scale = 100
    groups = defaultdict(list)
    counts = Counter()
    for row in rows:
        lat, lon = row.get('lat'), row.get('lon', row.get('lng'))
        try:
            x, y = math.floor(float(lat) * scale), math.floor(float(lon) * scale)
            if not math.isfinite(float(lat)) or not math.isfinite(float(lon)):
                continue
        except (TypeError, ValueError):
            continue
        key = f'{x}_{y}'
        groups[key].append(row)
        for d in row.get('discounts') or []:
            label = d.get('club') or d.get('club_name')
            if label:
                counts[label] += 1
    output = DOCS / 'nearby_shards'
    output.mkdir(exist_ok=True)
    manifest = {}
    for key, group in groups.items():
        digest = save(output / f'{key}-pending.json', group)
        target = output / f'{key}-{digest}.json'
        (output / f'{key}-pending.json').replace(target)
        manifest[key] = f'{key}-{digest}.json'
    save(DOCS / 'nearby_index.json', {'version': 1, 'scale': scale, 'cells': manifest,
                                     'labels': sorted(counts), 'club_counts': counts})
    print(f'Built {len(rows)} nearby branches in {len(manifest)} geographic cells')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', choices=('discounts', 'nearby'))
    args = parser.parse_args()
    if args.only != 'nearby':
        build_discounts()
    if args.only != 'discounts':
        build_nearby()
