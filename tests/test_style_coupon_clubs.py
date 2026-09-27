import pytest
import ashdod_port_scraper
import energy_club_scraper
import migdalor_club_scraper
import style_coupon_clubs as p
from extra_sources import EXTRA_SOURCE_MODULES

MODS = [ashdod_port_scraper, energy_club_scraper, migdalor_club_scraper]
BASE = 'https://example.test/'
HOME = '<a href="?page=category&id=7">מזון</a><a href="?page=category&id=81">שופינג</a>'

def tile(uid, title, text, button='לרכישה'):
    return f'<a href="/?page=Benefit&uuid={uid}"><div class="product-title">{title}</div><div class="product-desciption">{text}</div><span class="product-price">{button}</span></a>'

def test_coupon_parse_rejects_goods_and_billing_discounts():
    html = tile('ABCD-1234', 'שובר לרשת', 'לרכישה ב-₪80 בשווי ₪100') + tile('ABCD-1235', 'מכונת כביסה', 'לרכישה ב-₪400 בשווי ₪500') + tile('ABCD-1236', 'חנות', '5% הנחה', '5% הנחה')
    records = p.parse_category(html, BASE, 'club', '81', 'shopping', 'members')
    assert len(records) == 1
    assert records[0]['price'] == 80 and records[0]['original_price'] == 100
    assert records[0]['discount_type'] == 'coupon'
    assert records[0]['discount_url'] == BASE + '?page=Benefit&uuid=ABCD-1234'


def test_percent_voucher_and_experience():
    html = tile('ABCD-1234', 'שובר למסעדה', 'שוברים ב-15% הנחה') + tile('ABCD-1235', 'כרטיס כניסה לגן', 'לרכישה ב-₪60 בשווי ₪75')
    rows = p.parse_category(html, BASE, 'club', '7', 'food', '')
    assert len(rows) == 2
    assert rows[0]['discount_value'] == 15
    assert rows[1]['voucher_type'] == 'voucher'


def test_crawl_dedupes_and_fails_closed_on_missing_category():
    def fetch(url):
        if url == BASE:
            return HOME
        if url.endswith('id=7'):
            return HOME + tile('ABCD-1234', 'שובר למסעדה', 'ב-₪80 בשווי ₪100')
        return HOME + tile('ABCD-1234', 'שובר למסעדה', 'ב-₪80 בשווי ₪100')
    rows = p.crawl(BASE, 'club', fetch)
    assert len(rows) == 1
    with pytest.raises(ValueError, match='missing benefit tiles'):
        p.crawl(BASE, 'club', lambda u: HOME)


def test_modules_are_registered_and_use_home_page():
    for mod in MODS:
        assert mod.__name__ in EXTRA_SOURCE_MODULES
        seen = []
        def fake_fetch(url):
            seen.append(url)
            return '<html></html>'
        with pytest.raises(ValueError, match='missing'):
            mod.scrape(fake_fetch)
        assert seen == [mod.BASE_URL]
