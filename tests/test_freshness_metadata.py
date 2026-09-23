import main


def test_success_sets_dates_and_status():
    metadata = {}
    main.mark_source(metadata, "mcc", "2026-09-23T07:00:00Z", True, 10)
    entry = metadata["mcc"]
    assert entry["last_successful_scrape"] == "2026-09-23T07:00:00Z"
    assert entry["last_attempt"] == "2026-09-23T07:00:00Z"
    assert entry["status"] == "ok"
    assert entry["count"] == 10
    assert entry["club"] == "חבר"


def test_failure_keeps_true_date_and_marks_stale():
    metadata = {"hot": {"last_successful_scrape": "2026-09-16T06:00:01Z", "count": 50}}
    main.mark_source(metadata, "hot", "2026-09-23T07:00:00Z", False, error="403")
    entry = metadata["hot"]
    assert entry["last_successful_scrape"] == "2026-09-16T06:00:01Z"
    assert entry["last_attempt"] == "2026-09-23T07:00:00Z"
    assert entry["status"] == "stale"
    assert entry["error"] == "403"
    assert entry["count"] == 50


def test_failure_without_history_is_failed_and_recovery_clears_error():
    metadata = {}
    main.mark_source(metadata, "reshef", "t1", False, club="רשף")
    assert metadata["reshef"]["status"] == "failed"
    assert "last_successful_scrape" not in metadata["reshef"]
    main.mark_source(metadata, "reshef", "t2", True, 3)
    assert metadata["reshef"]["status"] == "ok"
    assert "error" not in metadata["reshef"]
    assert metadata["reshef"]["club"] == "רשף"


def test_build_freshness_lists_stale_sources_with_real_dates():
    metadata = {
        "all_combined": {"last_updated": "2026-09-23T07:05:00Z", "total_count": 5},
        "discount_type_counts": {"gift_card": 3},
    }
    main.mark_source(metadata, "mcc", "2026-09-23T07:00:00Z", True, 10)
    metadata["hot"] = {"last_successful_scrape": "2026-09-16T06:00:01Z"}
    main.mark_source(metadata, "hot", "2026-09-23T07:00:00Z", False)
    freshness = main.build_freshness(metadata)
    assert freshness["published_at"] == "2026-09-23T07:05:00Z"
    assert freshness["sources"] == {"mcc": "2026-09-23T07:00:00Z", "hot": "2026-09-16T06:00:01Z"}
    assert freshness["stale_sources"] == ["hot"]
    assert freshness["source_status"]["hot"]["club"] == "HOT"
    assert freshness["source_status"]["hot"]["status"] == "stale"
    assert "discount_type_counts" not in freshness["source_status"]


def test_legacy_entries_without_status_count_as_ok():
    metadata = {"amex": {"last_successful_scrape": "2026-09-20T00:00:00Z", "count": 1}}
    freshness = main.build_freshness(metadata)
    assert freshness["source_status"]["amex"]["status"] == "ok"
    assert freshness["stale_sources"] == []


def test_extra_source_failure_keeps_file_and_marks_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DISCOUNTS_DIR", str(tmp_path))
    (tmp_path / "demo_discounts.json").write_text('[{"club": "Demo", "business_name": "x"}]', encoding="utf-8")

    class Demo:
        SOURCE_KEY = "demo"
        CLUB_NAME = "Demo"

        @staticmethod
        def scrape():
            raise RuntimeError("blocked")

    metadata = {"demo": {"last_successful_scrape": "2026-09-01T00:00:00Z"}}
    data = main.run_extra_source(Demo, metadata, "2026-09-23T07:00:00Z")
    assert data == [{"club": "Demo", "business_name": "x"}]
    assert metadata["demo"]["status"] == "stale"
    assert metadata["demo"]["last_successful_scrape"] == "2026-09-01T00:00:00Z"
    assert metadata["demo"]["error"] == "blocked"
