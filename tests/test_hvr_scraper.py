from hvr_scraper import HEVER_DISCOUNT_VALUE, normalize_hvr_rechargeable_card_item


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

    # Sub-club label; the UI groups it under the "חבר" program (docs/programs.js).
    assert normalized["club"] == "חבר שלי"
    assert normalized["business_name"] == "SHASHA GIFTS"
    assert normalized["discount_type"] == "rechargeable_card"
    assert normalized["discount_value"] == HEVER_DISCOUNT_VALUE  # fixed Hever load discount
    # The discount text states the benefit, not the terms.
    assert normalized["discount"] == f"{HEVER_DISCOUNT_VALUE:g}% הנחה בטעינת כרטיס חבר שלי"
    assert "1,000" not in normalized["discount"]
    # Terms and description move to limitations.
    assert "1,000" in normalized["limitations"]
    assert "מתנות אישיות" in normalized["limitations"]


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

    # Sub-club label; the UI groups it under the "חבר" program (docs/programs.js).
    assert normalized["club"] == "חבר טעמים"
    assert normalized["business_name"] == "אנג'לינה פיצה ופסטה"
    assert normalized["discount_type"] == "rechargeable_card"
    assert normalized["discount_value"] == HEVER_DISCOUNT_VALUE  # fixed Hever load discount
    assert normalized["discount"] == f"{HEVER_DISCOUNT_VALUE:g}% הנחה בטעינת כרטיס חבר טעמים"
    assert normalized["limitations"] == ""


def test_percent_in_terms_does_not_replace_load_discount():
    # Real HVR wording: the remainder is paid on the credit card at 10% off.
    # That is a billing deal, not the prepaid card's load discount.
    item = {
        "company": "שגריר",
        "limitations": "ניתן לשלם עד 1,000 ₪ עם הכרטיס הנטען, והיתרה ב-10% הנחה במעמד חיוב כרטיס אשראי \"חבר\".",
    }

    normalized = normalize_hvr_rechargeable_card_item(item, source_name="giftcard")

    assert normalized["discount_value"] == HEVER_DISCOUNT_VALUE
    assert normalized["discount"].startswith(f"{HEVER_DISCOUNT_VALUE:g}%")
    assert "10%" in normalized["limitations"]


def test_discount_text_has_no_card_name_prefix():
    normalized = normalize_hvr_rechargeable_card_item(
        {"company": "DESIGUAL", "limitations": "עד 1000 שח לעסקה"}, source_name="giftcard"
    )

    assert not normalized["discount"].startswith("חבר שלי |")
    assert "|" not in normalized["discount"]
