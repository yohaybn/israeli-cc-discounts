import json

import dolcemaster_platform as platform
import paisplus_scraper as pais
import yours_scraper as yours


def page(products=None, categories=None, has_more='N'):
    return '<script>window.__PRELOADED_STATE__ = ' + json.dumps({
        'config': {'category': {'products': products or [], 'has_more': has_more},
                   'categories': categories or []}}) + ';</script>'


def test_public_crawl_visits_child_even_if_parent_fits_and_skips_login():
    tree = [{'category_id': 10, 'require_login': 'N', 'categories': [
        {'category_id': 11, 'require_login': 'N'}, {'category_id': 12, 'require_login': 'Y'}]}]
    calls = []
    def fetch(url):
        calls.append(url)
        if url.endswith('/category/11'):
            return page([{'product_id': 9, 'name': 'voucher'}])
        return page([{'product_id': 8, 'name': 'root'}], tree)
    result = platform.crawl_public_catalog('https://example.com', 10, fetch)
    assert {p['product_id'] for p in result} == {8, 9}
    assert all('/12' not in url for url in calls)
    assert len(calls) == 3


def test_truncated_leaf_fails_for_last_good_fallback():
    def fetch(url):
        return page([{'product_id': 1}], [{'category_id': 1, 'require_login': 'N'}], 'Y')
    import pytest
    with pytest.raises(ValueError, match='truncated'):
        platform.crawl_public_catalog('https://example.com', 1, fetch)


def test_parse_excludes_merchandise_expired_stock_and_non_savings():
    voucher = {'product_id': 55, 'name': 'תו קנייה 200 לרשת', 'product_type_id': 4,
               'product_type_name': 'תו כספי מנוהל', 'club_price': 160,
               'market_price': 200, 'out_of_stock': 'N'}
    products = [voucher, {**voucher, 'product_id': 56, 'product_type_id': 2},
                {**voucher, 'product_id': 57, 'out_of_stock': 'Y'},
                {**voucher, 'product_id': 58, 'club_price': 200}]
    for mod in [pais, yours]:
        records = mod.parse(products)
        assert len(records) == 1
        row = records[0]
        assert row['discount_type'] == 'coupon'
        assert row['discount_value'] is None
        assert row['price'] == 160 and row['original_price'] == 200
        assert row['discount_url'] == f'{mod.BASE_URL}/product/55'
        assert row['voucher_type'] == 'תו כספי מנוהל'


def test_yours_is_not_registered_until_truncated_leaves_can_be_paginated():
    from extra_sources import EXTRA_SOURCE_MODULES
    assert "yours_scraper" not in EXTRA_SOURCE_MODULES
    assert "paisplus_scraper" in EXTRA_SOURCE_MODULES
