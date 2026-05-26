from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

from ..core.load_jsonl import DuplicateKeyError, iter_jsonl_lines, parse_json_object
from ..core.models import Record, ValidationIssue, issue
from ..rules.expected_fields import LIST_STRING_FIELDS, REQUIRED_FIELD_ORDER, STRING_FIELDS


def _has_type_errors(raw: OrderedDict[str, Any]) -> bool:
    for field in STRING_FIELDS:
        if field not in raw or not isinstance(raw[field], str):
            return True
    if "authority_level" not in raw or isinstance(raw.get("authority_level"), bool) or not isinstance(raw.get("authority_level"), int):
        return True
    for field in LIST_STRING_FIELDS:
        value = raw.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            return True
    return False


def validate_jsonl_schema(path: Path) -> tuple[list[Record], list[ValidationIssue]]:
    records: list[Record] = []
    issues: list[ValidationIssue] = []

    try:
        line_iter = iter_jsonl_lines(path)
        for line_number, line in line_iter:
            raw: OrderedDict[str, Any] | None = None
            try:
                raw = parse_json_object(line)
            except DuplicateKeyError as exc:
                issues.append(
                    issue(
                        "BLOCKING",
                        "JSON_DUPLICATE_KEY",
                        "JSON object contains a duplicate key.",
                        "Each governed record key appears once.",
                        str(exc),
                        "Remove the duplicate key and keep the canonical field order.",
                        file=None,
                        line_number=line_number,
                    )
                )
                continue
            except Exception as exc:
                issues.append(
                    issue(
                        "BLOCKING",
                        "JSONL_SYNTAX",
                        "Line is not exactly one valid JSON object.",
                        "Each non-empty JSONL line parses as one JSON object.",
                        str(exc),
                        "Rewrite the line as one valid JSON object.",
                        file=None,
                        line_number=line_number,
                    )
                )
                continue

            keys = list(raw.keys())
            missing = [field for field in REQUIRED_FIELD_ORDER if field not in raw]
            extra = [field for field in keys if field not in REQUIRED_FIELD_ORDER]
            if missing:
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_MISSING_FIELD",
                        "Record is missing required schema fields.",
                        ", ".join(REQUIRED_FIELD_ORDER),
                        ", ".join(missing),
                        "Add the missing fields in canonical order.",
                        file=raw.get("file"),
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )
            if extra:
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_EXTRA_FIELD",
                        "Record contains fields outside the canonical schema.",
                        ", ".join(REQUIRED_FIELD_ORDER),
                        ", ".join(extra),
                        "Remove extra fields or encode meaning in governed statement fields.",
                        file=raw.get("file"),
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )
            if keys != REQUIRED_FIELD_ORDER:
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_FIELD_ORDER",
                        "Record fields are not in canonical order.",
                        ", ".join(REQUIRED_FIELD_ORDER),
                        ", ".join(keys),
                        "Rewrite the JSON object with fields in canonical order.",
                        file=raw.get("file"),
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )

            type_errors: list[str] = []
            for field in STRING_FIELDS:
                if field in raw and not isinstance(raw[field], str):
                    type_errors.append(f"{field}=not string")
            if "authority_level" in raw and (isinstance(raw["authority_level"], bool) or not isinstance(raw["authority_level"], int)):
                type_errors.append("authority_level=not int")
            for field in LIST_STRING_FIELDS:
                if field in raw:
                    if not isinstance(raw[field], list):
                        type_errors.append(f"{field}=not list")
                    elif any(not isinstance(item, str) for item in raw[field]):
                        type_errors.append(f"{field}=contains non-string item")
            if type_errors:
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_WRONG_TYPE",
                        "Record field has a non-canonical primitive type.",
                        "id/file/class/type/statement/violation/action/verification strings; authority_level int; scope/trace list[str].",
                        "; ".join(type_errors),
                        "Rewrite fields with the canonical primitive types.",
                        file=raw.get("file"),
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )

            empty_string_fields = [
                field
                for field in ["id", "statement", "violation", "action", "verification"]
                if isinstance(raw.get(field), str) and raw.get(field, "").strip() == ""
            ]
            if empty_string_fields:
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_EMPTY_REQUIRED_TEXT",
                        "Record contains an empty required text field.",
                        "id, statement, violation, action, and verification are non-empty strings.",
                        ", ".join(empty_string_fields),
                        "Fill each required text field with governed content.",
                        file=raw.get("file"),
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )

            trace_value = raw.get("trace")
            file_value = raw.get("file")
            if isinstance(trace_value, list) and not trace_value and file_value != "GOV-00":
                issues.append(
                    issue(
                        "BLOCKING",
                        "SCHEMA_EMPTY_TRACE",
                        "SRC/SRC-INDEX record has an empty trace array.",
                        "Only GOV-00 records may have empty trace arrays in SRC-only validation.",
                        "trace=[]",
                        "Trace the record to exact governing GOV/SRC record ids.",
                        file=file_value,
                        line_number=line_number,
                        record_id=raw.get("id"),
                    )
                )

            if not missing and not extra and not _has_type_errors(raw):
                records.append(Record.from_mapping(raw, path, line_number))
    except OSError as exc:
        issues.append(
            issue(
                "BLOCKING",
                "FILE_READ_FAILED",
                "Could not read governed JSONL file.",
                "Expected source files are readable UTF-8 JSONL.",
                str(exc),
                "Restore file readability and rerun the validator.",
                file=None,
                line_number=None,
            )
        )

    return records, issues

