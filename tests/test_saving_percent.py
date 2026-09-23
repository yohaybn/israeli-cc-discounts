from scraper_utils import saving_percent


def test_saving_percent():
    assert saving_percent("גיפט קארד ב-₪80 בשווי ₪100") == 20.0
    assert saving_percent("לרכישה ב-₪98 במקום ₪124") == 21.0
    assert saving_percent("25% הנחה") == 25
    assert saving_percent("החל מ-₪168") is None
    assert saving_percent("") is None
