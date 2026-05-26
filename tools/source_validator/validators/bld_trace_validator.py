from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..core.record_index import RecordIndex
from ..rules.allowed_tokens import SOURCE_FILE_IDS, SRC_INDEX_FILE
from ..rules.bld_registry import (
    BLD_INDEX_FILE,
    FILE_NAME_ONLY_TRACE_IDS,
    bld_record_family,
)

CROSS_CUTTING_TRACE_TERMS = {
    "SRC-04": ("idempot", "replay", "duplicate request"),
    "SRC-05": ("ledger", "journal", "invariant", "commit", "balance"),
    "SRC-06": ("failure", "reject", "invalid", "trap", "error", "condition"),
    "SRC-08": ("upgrade", "stable", "migration"),
    "SRC-09": ("api", "caller", "candid", "public method", "query", "update", "forbidden api"),
    "SRC-10": ("test", "proof", "review", "falsifier", "done", "acceptance"),
}


def validate_bld_trace_resolution(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if record.file != "GOV-00" and not record.trace:
            issues.append(
                issue(
                    "BLOCKING",
                    "TRACE_EMPTY",
                    "Governed non-GOV record has no governing trace.",
                    "Every non-GOV governed record traces to at least one exact upstream or allowed lateral record id.",
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
            if trace_id in FILE_NAME_ONLY_TRACE_IDS:
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
                        "Trace id does not resolve to any loaded GOV/SRC/BLD record.",
                        "Every trace item resolves to an existing governed record id.",
                        trace_id,
                        "Create or correct the governing record id, or remove the invalid trace.",
                        record,
                    )
                )

    return issues


def validate_bld_trace_direction(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        for trace_id in record.trace:
            target = index.record_by_id.get(trace_id)
            if not target:
                continue
            if target.authority_level > record.authority_level:
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_DIRECTION_INVALID",
                        "Trace points from higher authority to lower authority.",
                        "Trace references point upward or to allowed same-level records; lower authority cannot justify higher authority.",
                        f"{record.id} level {record.authority_level} -> {target.id} level {target.authority_level}",
                        "Replace the trace with a governing upstream record or move the claim to the lower authority file.",
                        record,
                    )
                )

    return issues


def _has_trace_to_file(record: Record, index: RecordIndex, file_id: str) -> bool:
    return any((target := index.record_by_id.get(trace_id)) and target.file == file_id for trace_id in record.trace)


def _has_controlling_target_trace(record: Record, index: RecordIndex) -> bool:
    for trace_id in record.trace:
        target = index.record_by_id.get(trace_id)
        if not target:
            continue
        if target.file in SOURCE_FILE_IDS or target.file == SRC_INDEX_FILE:
            return True
        if target.file == BLD_INDEX_FILE and target.id.startswith(
            ("BLD-INDEX-SRC-ROUTE-", "BLD-INDEX-MANIFEST-", "BLD-INDEX-TRACE-")
        ):
            return True
    return False


def validate_bld_target_traces(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if not record.file.startswith("BLD-") or record.file in {"BLD-INDEX", "BLD-00"}:
            continue
        family = bld_record_family(record.id, record.file)
        if family == "TARGET" and not _has_controlling_target_trace(record, index):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_TARGET_MISSING_CONTROLLING_TRACE",
                    "BLD implementation TARGET record lacks controlling SRC or BLD-INDEX route trace.",
                    "TARGET records trace to at least one exact SRC/SRC-INDEX record or BLD-INDEX route record.",
                    ", ".join(record.trace) if record.trace else "trace=[]",
                    "Trace the TARGET record to controlling source authority or a BLD-INDEX route record.",
                    record,
                )
            )

        if family not in {"TARGET", "CONTRACT", "PIPELINE", "STRUCTURE", "STATE", "DATA", "FAILURE", "FORBID", "TEST", "REVIEW", "STOP"}:
            continue
        text = " ".join([record.id, record.statement, record.violation, record.verification]).lower()
        for file_id, terms in CROSS_CUTTING_TRACE_TERMS.items():
            if any(term in text for term in terms) and not _has_trace_to_file(record, index, file_id):
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_CROSS_CUTTING_TRACE_MISSING",
                        "BLD implementation record mentions a cross-cutting source concern without tracing to that SRC file.",
                        f"Terms {terms} require trace coverage from {file_id} when applicable.",
                        f"{record.id} traces to {record.trace}",
                        f"Add an exact controlling {file_id} record trace or remove the unsupported cross-cutting claim.",
                        record,
                    )
                )

    return issues

