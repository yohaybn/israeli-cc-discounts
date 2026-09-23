import json
import os
import unittest

# data/ is generated locally and git-ignored; docs/data/ holds the committed published copy.
COMBINED_PATHS = (
    "data/discounts/all_combined_discounts.json",
    "docs/data/all_combined_discounts.json",
)


def normalize_value(value):
    if value is None:
        return ""
    return str(value).strip().lower().replace("\u00a0", " ")


def combined_path():
    for path in COMBINED_PATHS:
        if os.path.exists(path):
            return path
    return None


class CombinedDiscountsDeduplicationTest(unittest.TestCase):
    def test_combined_discounts_are_not_duplicated(self):
        path = combined_path()
        if path is None:
            self.skipTest("no combined dataset generated or published")
        with open(path, encoding="utf-8") as f:
            records = json.load(f)

        seen = set()
        duplicates = []
        for record in records:
            key = (
                normalize_value(record.get("club")),
                normalize_value(record.get("business_name")),
                normalize_value(record.get("discount")),
                normalize_value(record.get("discount_url")),
                normalize_value(record.get("discount_type")),
                normalize_value(record.get("discount_value")),
            )
            if key in seen:
                duplicates.append((record.get("business_name"), record.get("discount")))
            seen.add(key)

        self.assertFalse(duplicates, f"Duplicate records found in {path}: {duplicates[:5]}")


if __name__ == "__main__":
    unittest.main()
