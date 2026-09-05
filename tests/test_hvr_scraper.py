from hvr_scraper import normalize_hvr_rechargeable_card_item


def test_normalize_giftcard_item():
    item = {
        "company": " SHASHA GIFTS ",
        "website": "www.shashagifts.com",
        "company_desc": "אתר אונליין למתנות אישיות מעוצבות",
        "limitations": "עד 1,000 ש\"ח לעסקה ",
        "online_limitations": "עד 1,000 ש\"ח לעסקה ",
        "product_types": "מתנות מודפסות,מוצרי טיפוח",
        "branch_qty": 1,
    }

    normalized = normalize_hvr_rechargeable_card_item(item, source_name="giftcard")

    assert normalized["club"] == "חבר"
    assert normalized["business_name"] == "SHASHA GIFTS"
    assert normalized["discount_type"] == "rechargeable_card"
    assert normalized["discount_value"] is None
    assert "חבר שלי" in normalized["discount"]
    assert "1,000" in normalized["discount"] or "חבר שלי" in normalized["discount"]


def test_normalize_branch_item():
    item = {
        "name": "אנג'לינה פיצה ופסטה",
        "city": "אילת",
        "address": "טיילת המלך",
        "website": "angelinapizzapasta.rest.co.il",
        "limitations": "",
        "search_words": "פיצה, pizza_search, אנג'לינה",
        "product_types": "אוכל איטלקי,פיצה",
    }

    normalized = normalize_hvr_rechargeable_card_item(item, source_name="teamimcard_branches")

    assert normalized["club"] == "חבר"
    assert normalized["business_name"] == "אנג'לינה פיצה ופסטה"
    assert normalized["discount_type"] == "rechargeable_card"
    assert normalized["discount_value"] is None
    assert "חבר טעמים" in normalized["discount"]
    assert "אילת" in normalized["discount"] or "חבר טעמים" in normalized["discount"]
