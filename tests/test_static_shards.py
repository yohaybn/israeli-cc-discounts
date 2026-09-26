"""Static Pages indexes round-trip the real fixture without dropping offers."""
import json
from scripts.build_static_shards import build_discounts, build_nearby


def test_discount_shards_roundtrip(tmp_path, monkeypatch):
    import scripts.build_static_shards as sh
    monkeypatch.setattr(sh, 'DOCS', tmp_path)
    rows = [
        {'club': 'MCC', 'business_name': 'חנות א', 'discount': '10%', 'discount_value': 10},
        {'club': 'HOT', 'business_name': 'חנות א', 'discount': '15%', 'discount_value': 15},
        {'club': 'MCC', 'business_name': 'חנות ב', 'discount': 'שובר', 'discount_type': 'voucher'},
    ]
    (tmp_path / 'all_combined_discounts.json').write_text(json.dumps(rows, ensure_ascii=False))
    build_discounts()
    index = json.loads((tmp_path / 'business_index.json').read_text())
    assert index['total'] == 3
    assert len(index['businesses']) == 2
    a = next(b for b in index['businesses'] if b['business_name'] == 'חנות א')
    assert a['best_discount_value'] == 15
    assert a['club_counts'] == {'MCC': 1, 'HOT': 1}
    data = json.loads((tmp_path / 'discount_shards' / index['shards'][a['shard']]).read_text())
    assert data['חנות א'] == rows[:2]
    assert sum(len(json.loads((tmp_path / 'discount_shards' / path).read_text())[name])
               for path in index['shards'].values()
               for name in json.loads((tmp_path / 'discount_shards' / path).read_text())) == len(rows)


def test_nearby_cell_boundaries(tmp_path, monkeypatch):
    import scripts.build_static_shards as sh
    monkeypatch.setattr(sh, 'DOCS', tmp_path)
    rows = [{'lat': 31.9999, 'lon': 34.9999, 'discounts': [{'club': 'MCC'}]},
            {'lat': 32.0001, 'lon': 35.0001, 'discounts': [{'club': 'HOT'}]}]
    (tmp_path / 'businesses_with_discounts.json').write_text(json.dumps(rows))
    build_nearby()
    index = json.loads((tmp_path / 'nearby_index.json').read_text())
    assert index['scale'] == 100
    assert sum(len(json.loads((tmp_path / 'nearby_shards' / path).read_text()))
               for path in index['cells'].values()) == 2
    assert '3199_3499' in index['cells'] and '3200_3500' in index['cells']
