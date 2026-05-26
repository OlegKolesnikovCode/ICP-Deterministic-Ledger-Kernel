from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..core.record_index import RecordIndex
from ..rules.file_registry import EXPECTED_FILE_IDS


def validate_trace_resolution(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    file_name_only = set(EXPECTED_FILE_IDS)

    for record in records:
        if record.file != "GOV-00" and not record.trace:
            issues.append(
                issue(
                    "BLOCKING",
                    "TRACE_EMPTY",
                    "SRC/SRC-INDEX record has no governing trace.",
                    "Every non-GOV source record traces to at least one exact record id.",
                    "trace=[]",
                    "Add exact trace record ids.",
                    record,
                )
            )
        for trace_id in record.trace:
            if not trace_id:
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_EMPTY_ITEM",
                        "Trace array contains an empty trace id.",
                        "Trace items are non-empty governed record ids.",
                        "empty string",
                        "Remove empty trace items or replace them with exact record ids.",
                        record,
                    )
                )
                continue
            if trace_id in file_name_only:
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_FILE_NAME_ONLY",
                        "Trace cites a governed file id instead of a governed record id.",
                        "Trace targets exact record ids.",
                        trace_id,
                        "Replace the file-level trace with the exact controlling record id.",
                        record,
                    )
                )
                continue
            if trace_id.startswith("BLD-"):
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_TO_BLD",
                        "SRC-only source record traces to a BLD record.",
                        "SRC authority may not depend on BLD records in this phase.",
                        trace_id,
                        "Replace the trace with the controlling GOV/SRC source record or move the dependency to BLD validation later.",
                        record,
                    )
                )
                continue
            if trace_id == record.id:
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_SELF_REFERENCE",
                        "Record traces to itself.",
                        "Self-tracing is forbidden unless an explicit GOV rule allows it.",
                        trace_id,
                        "Trace to the higher-level controlling record instead.",
                        record,
                    )
                )
                continue
            if trace_id not in index.record_by_id:
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_UNRESOLVED",
                        "Trace id does not resolve to any GOV/SRC/SRC-INDEX record loaded in SRC-only mode.",
                        "Every trace item resolves to an existing governed record id.",
                        trace_id,
                        "Create or correct the governing source record id, or remove the invalid trace.",
                        record,
                    )
                )

    return issues

