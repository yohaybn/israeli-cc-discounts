import json
import types

import main
from extra_sources import EXTRA_SOURCE_MODULES, load_extra_sources


def _fake_module(records=None, error=None):
    module = types.SimpleNamespace(SOURCE_KEY="fake_source", CLUB_NAME="Fake")

    def scrape():
        if error:
            raise error
        return records or []

    module.scrape = scrape
    return module


def test_registered_modules_follow_the_contract():
    modules = load_extra_sources()
    assert len(modules) == len(EXTRA_SOURCE_MODULES)
    keys = set()
    for module in modules:
        assert module.SOURCE_KEY and module.SOURCE_KEY not in keys
        keys.add(module.SOURCE_KEY)
        assert module.CLUB_NAME
        assert callable(module.scrape)
        assert callable(module.fetch_raw)


def test_run_extra_source_saves_fresh_data(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DISCOUNTS_DIR", str(tmp_path))
    metadata = {}
    records = [{"club": "Fake", "business_name": "A"}]
    result = main.run_extra_source(_fake_module(records), metadata, "2026-09-23T00:00:00Z")
    assert result == records
    assert metadata["fake_source"]["count"] == 1
    saved = json.loads((tmp_path / "fake_source_discounts.json").read_text(encoding="utf-8"))
    assert saved == records


def test_run_extra_source_keeps_last_good_data_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DISCOUNTS_DIR", str(tmp_path))
    previous = [{"club": "Fake", "business_name": "Old"}]
    (tmp_path / "fake_source_discounts.json").write_text(json.dumps(previous), encoding="utf-8")
    metadata = {}
    result = main.run_extra_source(_fake_module(error=RuntimeError("403")), metadata, "now")
    assert result == previous
    assert "fake_source" not in metadata
    result = main.run_extra_source(_fake_module([]), metadata, "now")
    assert result == previous
