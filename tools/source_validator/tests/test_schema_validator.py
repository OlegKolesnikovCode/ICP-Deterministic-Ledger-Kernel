import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.validators.schema_validator import validate_jsonl_schema


class SchemaValidatorTests(unittest.TestCase):
    def test_invalid_jsonl_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl"
            path.write_text('{"id":"PROJECT-001", bad json\n', encoding="utf-8")

            records, issues = validate_jsonl_schema(path)

        self.assertEqual(records, [])
        self.assertTrue(any(issue.category == "JSONL_SYNTAX" and issue.severity == "BLOCKING" for issue in issues))

    def test_missing_field_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl"
            path.write_text(
                '{"id":"PROJECT-001","file":"SRC-00","class":"SOURCE","type":"DECLARES",'
                '"scope":["SRC-00"],"authority_level":2,"statement":"A statement.",'
                '"violation":"Violation.","action":"ACTION","verification":"Verify."}\n',
                encoding="utf-8",
            )

            _records, issues = validate_jsonl_schema(path)

        self.assertTrue(any(issue.category == "SCHEMA_MISSING_FIELD" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()
