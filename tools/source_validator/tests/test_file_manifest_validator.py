import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.validators.file_manifest_validator import validate_file_manifest
from source_validator.rules.file_registry import EXPECTED_FILE_NAMES
from helpers import make_record


class FileManifestValidatorTests(unittest.TestCase):
    def test_record_file_must_match_containing_filename(self):
        record = make_record("PROJECT-FILE-001", "SRC-01")
        record = make_record("PROJECT-FILE-001", "SRC-01")
        object.__setattr__(record, "source_path", Path("SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl"))

        issues = validate_file_manifest({name: Path("missing") for name in EXPECTED_FILE_NAMES}, [record])

        self.assertTrue(any(issue.category == "FILE_ID_MISMATCH" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()
