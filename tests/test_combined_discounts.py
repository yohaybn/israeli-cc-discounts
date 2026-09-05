import json
import unittest


def normalize_value(value):
    if value is None:
        return ""
    return str(value).strip().lower().replace("\u00a0", " ")


class CombinedDiscountsDeduplicationTest(unittest.TestCase):
    def test_combined_discounts_are_not_duplicated(self):
        with open("data/all_combined_discounts.json", encoding="utf-8") as f:
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

        self.assertFalse(duplicates, f"Duplicate records found: {duplicates[:5]}")


if __name__ == "__main__":
    unittest.main()
