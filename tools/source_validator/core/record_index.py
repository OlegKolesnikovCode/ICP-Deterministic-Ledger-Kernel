from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import Record, ValidationIssue, issue


@dataclass
class RecordIndex:
    record_by_id: dict[str, Record]
    records_by_file: dict[str, list[Record]]
    inbound_traces: dict[str, list[str]]
    outbound_traces: dict[str, list[str]]
    records_by_prefix: dict[str, list[Record]]
    issues: list[ValidationIssue]


def extract_record_prefix(record_id: str) -> str:
    parts = record_id.split("-")
    if len(parts) < 2:
        return record_id
    if parts[0] == "SRC" and len(parts) > 2 and parts[1] == "INDEX":
        return "SRC-INDEX"
    return parts[0]


def build_record_index(records: list[Record]) -> RecordIndex:
    record_by_id: dict[str, Record] = {}
    records_by_file: dict[str, list[Record]] = defaultdict(list)
    inbound_traces: dict[str, list[str]] = defaultdict(list)
    outbound_traces: dict[str, list[str]] = defaultdict(list)
    records_by_prefix: dict[str, list[Record]] = defaultdict(list)
    issues: list[ValidationIssue] = []
    ids_by_file: dict[tuple[str, str], Record] = {}

    for record in records:
        if "-" not in record.id:
            issues.append(
                issue(
                    "BLOCKING",
                    "ID_FORMAT_INVALID",
                    "Record id does not contain a namespace separator.",
                    "Record ids use governed uppercase namespace tokens separated by hyphens.",
                    record.id,
                    "Rename the record to a governed namespace id and update traces.",
                    record,
                )
            )

        existing = record_by_id.get(record.id)
        if existing:
            issues.append(
                issue(
                    "BLOCKING",
                    "DUPLICATE_RECORD_ID",
                    "Record id is duplicated globally.",
                    "Every governed record id is globally unique.",
                    f"{existing.source_path}:{existing.line_number} and {record.source_path}:{record.line_number}",
                    "Rename one record and update all traces to the surviving id.",
                    record,
                )
            )
        else:
            record_by_id[record.id] = record

        file_key = (record.file, record.id)
        existing_in_file = ids_by_file.get(file_key)
        if existing_in_file:
            issues.append(
                issue(
                    "BLOCKING",
                    "DUPLICATE_RECORD_ID_IN_FILE",
                    "Record id is duplicated within the same governed file.",
                    "Each governed file defines a record id at most once.",
                    f"{existing_in_file.source_path}:{existing_in_file.line_number} and {record.source_path}:{record.line_number}",
                    "Rename or remove the duplicate record.",
                    record,
                )
            )
        else:
            ids_by_file[file_key] = record

        records_by_file[record.file].append(record)
        records_by_prefix[extract_record_prefix(record.id)].append(record)
        outbound_traces[record.id] = list(record.trace)
        for trace_id in record.trace:
            inbound_traces[trace_id].append(record.id)

    return RecordIndex(
        record_by_id=record_by_id,
        records_by_file=dict(records_by_file),
        inbound_traces=dict(inbound_traces),
        outbound_traces=dict(outbound_traces),
        records_by_prefix=dict(records_by_prefix),
        issues=issues,
    )

