import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.core.record_index import build_record_index
from source_validator.validators.trace_direction_validator import validate_trace_direction
from source_validator.validators.trace_resolution_validator import validate_trace_resolution
from helpers import make_record


class TraceDirectionValidatorTests(unittest.TestCase):
    def test_src_trace_to_bld_is_blocking(self):
        record = make_record("PROJECT-SCOPE-001", "SRC-00", trace=["BLD-00-IMPLEMENTATION-001"])
        index = build_record_index([record])

        resolution_issues = validate_trace_resolution([record], index)
        direction_issues = validate_trace_direction([record], index)

        self.assertTrue(any(issue.category == "TRACE_TO_BLD" and issue.severity == "BLOCKING" for issue in resolution_issues))
        self.assertTrue(any(issue.category == "TRACE_DIRECTION_TO_BLD" and issue.severity == "BLOCKING" for issue in direction_issues))


if __name__ == "__main__":
    unittest.main()
