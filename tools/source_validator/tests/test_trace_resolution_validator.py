import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.core.record_index import build_record_index
from source_validator.validators.trace_resolution_validator import validate_trace_resolution
from helpers import make_record


class TraceResolutionValidatorTests(unittest.TestCase):
    def test_duplicate_record_id_is_blocking(self):
        records = [
            make_record("PROJECT-DUP-001", "SRC-00", trace=["GOV-META-000"], line_number=1),
            make_record("PROJECT-DUP-001", "SRC-00", trace=["GOV-META-000"], line_number=2),
        ]

        index = build_record_index(records)

        self.assertTrue(any(issue.category == "DUPLICATE_RECORD_ID" and issue.severity == "BLOCKING" for issue in index.issues))

    def test_unresolved_trace_is_blocking(self):
        record = make_record("PROJECT-SCOPE-001", "SRC-00", trace=["GOV-DOES-NOT-EXIST"])
        index = build_record_index([record])

        issues = validate_trace_resolution([record], index)

        self.assertTrue(any(issue.category == "TRACE_UNRESOLVED" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()
