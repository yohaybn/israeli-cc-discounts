import os
import unittest


class DataLayoutTest(unittest.TestCase):
    def test_docs_data_contains_only_frontend_files(self):
        frontend_files = {
            "docs/data/all_combined_discounts.json",
            "docs/data/businesses_with_discounts.json",
            "docs/data/data_freshness.json",
        }
        forbidden_files = {
            "docs/data/mcc_discounts.json",
            "docs/data/hot_discounts.json",
            "docs/data/htzone_discounts.json",
            "docs/data/buyme_discounts.json",
            "docs/data/hvr_rechargeable_cards.json",
            "docs/data/scrape_metadata.json",
            "docs/data/unmatched_discounts.json",
        }

        missing = sorted(path for path in frontend_files if not os.path.exists(path))
        self.assertFalse(missing, f"Missing published frontend files: {missing}")
        leaked = sorted(path for path in forbidden_files if os.path.exists(path))
        self.assertFalse(leaked, f"Per-source files must not be published under docs/data: {leaked}")

        businesses_dir = "docs/data/businesses"
        if os.path.isdir(businesses_dir):
            region_files = {
                "docs/data/businesses/businesses_center.json",
                "docs/data/businesses/businesses_north.json",
                "docs/data/businesses/businesses_south.json",
                "docs/data/businesses/businesses_eilat_arava.json",
            }
            self.assertTrue(any(os.path.exists(path) for path in region_files))

    def test_generated_per_source_files_live_under_data_discounts(self):
        # data/ is git-ignored and only exists after a local run of main.py.
        if not os.path.isdir("data/discounts"):
            self.skipTest("data/discounts not generated in this checkout")
        self.assertTrue(os.path.exists("data/discounts/all_combined_discounts.json"))
        self.assertFalse(os.path.exists("data/mcc_discounts.json"), "per-source files moved to data/discounts/")


if __name__ == "__main__":
    unittest.main()
