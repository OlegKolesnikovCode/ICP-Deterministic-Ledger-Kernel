from __future__ import annotations

from pathlib import Path

from ..core.models import Record, ValidationIssue, issue
from ..rules.bld_registry import (
    BLD_00_FILE_NAME,
    BLD_CONTROL_FILE_IDS,
    BLD_INDEX_FILE,
    BLD_INDEX_FILE_NAME,
    EXPECTED_BLD_AUTHORITY_LEVEL,
    EXPECTED_BLD_CLASS,
    REQUIRED_BLD_INDEX_RECORD_IDS,
    bld_file_id_from_filename,
    canonical_bld_meta_statement,
    statement_key_values,
)


def _manifest_targets(records: list[Record]) -> dict[str, str]:
    targets = {
        BLD_INDEX_FILE: BLD_INDEX_FILE_NAME,
        "BLD-00": BLD_00_FILE_NAME,
    }
    for record in records:
        if record.file != BLD_INDEX_FILE or not record.id.startswith("BLD-INDEX-MANIFEST-"):
            continue
        fields = statement_key_values(record.statement)
        target_scope = fields.get("target_scope")
        target_file = fields.get("target_file")
        if target_scope and target_file:
            targets[target_scope] = target_file
    return targets


def validate_bld_file_manifest(
    bld_paths: list[Path],
    records: list[Record],
    index_record_ids: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    manifest_targets = _manifest_targets(records)
    records_by_path: dict[Path, list[Record]] = {}

    for record in records:
        if not record.file.startswith("BLD-"):
            continue
        records_by_path.setdefault(record.source_path, []).append(record)

        expected_file_id = bld_file_id_from_filename(record.source_path.name)
        if expected_file_id and record.file != expected_file_id:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILE_ID_MISMATCH",
                    "BLD record file field does not match the containing governed filename.",
                    expected_file_id,
                    record.file,
                    "Move the record to the owning BLD file or correct the file field.",
                    record,
                )
            )

        if record.file not in BLD_CONTROL_FILE_IDS:
            issues.append(
                issue(
                    "BLOCKING",
                    "UNKNOWN_BLD_FILE_ID",
                    "BLD record declares a file id outside the GOV-authorized BLD range.",
                    "BLD-INDEX or BLD-00 through BLD-10.",
                    record.file,
                    "Move the record to an authorized BLD file id or update GOV-00 before validation.",
                    record,
                )
            )
            continue

        expected_class = EXPECTED_BLD_CLASS[record.file]
        if record.class_name != expected_class:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILE_CLASS_MISMATCH",
                    "BLD record class does not match the governed BLD file registry.",
                    expected_class,
                    record.class_name,
                    "Correct the class field to the BLD file registry value.",
                    record,
                )
            )

        expected_level = EXPECTED_BLD_AUTHORITY_LEVEL[record.file]
        if record.authority_level != expected_level:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_AUTHORITY_LEVEL_MISMATCH",
                    "BLD record authority_level does not match GOV-00 BLD authority order.",
                    str(expected_level),
                    str(record.authority_level),
                    "Correct authority_level to the governed BLD file registry value.",
                    record,
                )
            )

        expected_filename = manifest_targets.get(record.file)
        if expected_filename and record.source_path.name != expected_filename:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILENAME_MISMATCH",
                    "BLD file name does not match the BLD-INDEX manifest route.",
                    expected_filename,
                    record.source_path.name,
                    "Rename the BLD file or correct the BLD-INDEX manifest route under GOV authority.",
                    record,
                )
            )

    if not any(path.name == BLD_INDEX_FILE_NAME for path in bld_paths):
        issues.append(
            issue(
                "BLOCKING",
                "MISSING_BLD_INDEX",
                "BLD validation requires the governed BLD-INDEX router/enforcer file.",
                BLD_INDEX_FILE_NAME,
                "not found",
                "Restore BLD-INDEX before validating or generating BLD files.",
                file=BLD_INDEX_FILE,
            )
        )

    for path in bld_paths:
        file_id = bld_file_id_from_filename(path.name)
        if file_id is None:
            issues.append(
                issue(
                    "BLOCKING",
                    "UNAUTHORIZED_BLD_FILENAME",
                    "BLD JSONL filename is outside the authorized BLD control-file range.",
                    "BLD-INDEX or BLD-00 through BLD-10 filename prefix.",
                    path.name,
                    "Rename the file to an authorized BLD file id or remove it from governed sources.",
                    file=None,
                )
            )
            continue

        path_records = records_by_path.get(path, [])
        if not path_records:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILE_EMPTY",
                    "BLD JSONL file contains no valid governed records.",
                    "Every active BLD file contains at least the canonical FILE metadata record.",
                    path.name,
                    "Restore the governed BLD records or remove the empty file.",
                    file=file_id,
                )
            )
            continue

        canonical = canonical_bld_meta_statement(file_id)
        meta_records = [record for record in path_records if record.statement == canonical]
        if len(meta_records) != 1:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILE_META_COUNT_INVALID",
                    "BLD file does not contain exactly one canonical FILE metadata record.",
                    canonical,
                    f"{len(meta_records)} canonical FILE metadata records",
                    "Add exactly one canonical FILE metadata declaration and remove duplicates.",
                    file=file_id,
                    line_number=path_records[0].line_number,
                )
            )
        elif path_records[0].id != meta_records[0].id:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FILE_META_NOT_FIRST",
                    "BLD file canonical FILE metadata record is not the first record.",
                    "The first non-empty JSONL record declares canonical FILE metadata.",
                    f"{meta_records[0].id} at line {meta_records[0].line_number}",
                    "Move the canonical FILE metadata record to the top of the BLD file.",
                    meta_records[0],
                )
            )

    missing_index_records = [record_id for record_id in REQUIRED_BLD_INDEX_RECORD_IDS if record_id not in index_record_ids]
    for record_id in missing_index_records:
        issues.append(
            issue(
                "BLOCKING",
                "BLD_INDEX_REQUIRED_RECORD_MISSING",
                "BLD-INDEX is missing a governed BLD template/codegen/enforcer record.",
                record_id,
                "missing",
                "Restore the required BLD-INDEX template, validation, trace, or stop record.",
                file=BLD_INDEX_FILE,
                record_id=record_id,
            )
        )

    return issues

