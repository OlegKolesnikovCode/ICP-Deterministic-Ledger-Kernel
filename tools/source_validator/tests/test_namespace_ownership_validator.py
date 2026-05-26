import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.validators.namespace_ownership_validator import validate_namespace_ownership
from helpers import make_record


class NamespaceOwnershipValidatorTests(unittest.TestCase):
    def test_wrong_namespace_owner_is_blocking(self):
        record = make_record("TRANSFER-RULE-001", "SRC-02", trace=["GOV-META-000"])

        issues = validate_namespace_ownership([record])

        self.assertTrue(any(issue.category == "NAMESPACE_OWNER_MISMATCH" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()
