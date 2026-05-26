import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.core.record_index import build_record_index
from source_validator.validators.src10_usage_validator import validate_src10_usage
from helpers import make_record


class Src10UsageValidatorTests(unittest.TestCase):
    def test_src10_scope_leakage_is_blocking(self):
        record = make_record(
            "TEST-SCOPE-001",
            "SRC-10",
            statement="SRC-10 defines project scope for ledger behavior.",
            trace=["PROJECT-SCOPE-001"],
        )
        source = make_record("PROJECT-SCOPE-001", "SRC-00", trace=["GOV-META-000"])
        index = build_record_index([record, source])

        issues = validate_src10_usage([record, source], index)

        self.assertTrue(any(issue.category == "SRC10_CREATES_SOURCE_TRUTH" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()
