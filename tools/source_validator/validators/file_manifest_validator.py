from __future__ import annotations

from pathlib import Path

from ..core.models import Record, ValidationIssue, issue
from ..rules.file_registry import (
    EXPECTED_AUTHORITY_LEVEL,
    EXPECTED_FILE_CLASS,
    EXPECTED_FILE_NAMES,
    NAME_TO_FILE_ID,
    canonical_file_meta_statement,
    file_id_from_filename,
)


def validate_file_manifest(expected_paths: dict[str, Path], records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for filename in EXPECTED_FILE_NAMES:
        if not expected_paths[filename].exists():
            expected_id = NAME_TO_FILE_ID[filename]
            issues.append(
                issue(
                    "BLOCKING",
                    "MISSING_REQUIRED_SOURCE_FILE",
                    "Required GOV/SRC source file is missing from the SRC-only validation set.",
                    filename,
                    "not found",
                    "Restore the expected governed source file before BLD generation.",
                    file=expected_id,
                )
            )

    records_by_path: dict[Path, list[Record]] = {}
    for record in records:
        records_by_path.setdefault(record.source_path, []).append(record)

        expected_file = file_id_from_filename(record.source_path.name)
        if expected_file and record.file != expected_file:
            issues.append(
                issue(
                    "BLOCKING",
                    "FILE_ID_MISMATCH",
                    "Record file field does not match the containing governed filename.",
                    expected_file,
                    record.file,
                    "Move the record to the owning file or correct the file field.",
                    record,
                )
            )

        if record.file not in EXPECTED_FILE_CLASS:
            issues.append(
                issue(
                    "BLOCKING",
                    "UNKNOWN_GOVERNED_FILE_ID",
                    "Record declares a file id outside the SRC-only validator registry.",
                    "GOV-00, SRC-INDEX, or SRC-00 through SRC-10.",
                    record.file,
                    "Move this record out of the SRC-only set or add the governed file in a later phase.",
                    record,
                )
            )
            continue

        expected_class = EXPECTED_FILE_CLASS[record.file]
        if record.class_name != expected_class:
            issues.append(
                issue(
                    "BLOCKING",
                    "FILE_CLASS_MISMATCH",
                    "Record class does not match the governed file registry.",
                    expected_class,
                    record.class_name,
                    "Correct the class field to the file registry value.",
                    record,
                )
            )

        expected_level = EXPECTED_AUTHORITY_LEVEL[record.file]
        if record.authority_level != expected_level:
            issues.append(
                issue(
                    "BLOCKING",
                    "AUTHORITY_LEVEL_MISMATCH",
                    "Record authority_level does not match the governed file registry.",
                    str(expected_level),
                    str(record.authority_level),
                    "Correct authority_level to the file registry value.",
                    record,
                )
            )

    for filename, path in expected_paths.items():
        if not path.exists():
            continue
        path_records = records_by_path.get(path, [])
        expected_file = file_id_from_filename(filename)
        if not expected_file:
            continue
        canonical = canonical_file_meta_statement(expected_file)
        meta_records = [record for record in path_records if record.statement == canonical]
        if len(meta_records) != 1:
            issues.append(
                issue(
                    "BLOCKING",
                    "FILE_META_COUNT_INVALID",
                    "Governed file does not contain exactly one canonical FILE metadata record.",
                    canonical,
                    f"{len(meta_records)} canonical FILE metadata records",
                    "Add exactly one canonical first-record metadata declaration and remove duplicates.",
                    file=expected_file,
                    line_number=path_records[0].line_number if path_records else None,
                )
            )

    return issues
