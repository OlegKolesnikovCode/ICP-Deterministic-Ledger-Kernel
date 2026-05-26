from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..core.record_index import RecordIndex


def _is_file_meta(record: Record) -> bool:
    return record.statement.startswith(f"file_id={record.file};")


def _has_inbound_from_prefix(index: RecordIndex, record_id: str, prefixes: tuple[str, ...]) -> bool:
    inbound_ids = index.inbound_traces.get(record_id, [])
    for inbound_id in inbound_ids:
        if inbound_id.startswith(prefixes):
            return True
    return False


def validate_src_coverage(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if record.file not in ("GOV-00", "SRC-INDEX") and not _is_file_meta(record):
            if not index.inbound_traces.get(record.id):
                issues.append(
                    issue(
                        "INFO",
                        "SOURCE_RECORD_ZERO_INBOUND_TRACES",
                        "Source record has zero inbound traces in the current SRC-only graph.",
                        "Important source records are normally routed, tested, or depended on downstream.",
                        "0 inbound traces",
                        "Review whether this is intentionally terminal or should be referenced by routing/tests/DoD.",
                        record,
                    )
                )

        if record.id.startswith("INV-") and not _has_inbound_from_prefix(index, record.id, ("TEST-", "DONE-")):
            issues.append(
                issue(
                    "WARNING",
                    "INVARIANT_NOT_REFERENCED_BY_TEST_OR_DONE",
                    "Invariant record is not referenced by TEST-* or DONE-* records.",
                    "INV-* records should normally be covered by proof or Definition of Done records.",
                    "no TEST-/DONE- inbound trace",
                    "Add SRC-10 proof/DoD coverage or document why no proof routing is required.",
                    record,
                )
            )
        if record.id.startswith("FAIL-") and not _has_inbound_from_prefix(index, record.id, ("TEST-", "LIFE-", "TRANSFER-", "FAIL-")):
            issues.append(
                issue(
                    "WARNING",
                    "FAILURE_RULE_NOT_REFERENCED",
                    "Failure model record is not referenced by tests or operation/failure rules.",
                    "FAIL-* records should normally be covered by tests or operation/failure routing.",
                    "no relevant inbound trace",
                    "Add proof or operation/failure references where appropriate.",
                    record,
                )
            )
        if record.id.startswith(("API-", "FORBID-")) and not _has_inbound_from_prefix(index, record.id, ("TEST-", "SRC-INDEX-")):
            issues.append(
                issue(
                    "WARNING",
                    "API_RULE_NOT_ROUTED_OR_TESTED",
                    "API/FORBID record is not referenced by tests or SRC-INDEX routing.",
                    "API/FORBID rules should be routed or test-covered.",
                    "no TEST-/SRC-INDEX inbound trace",
                    "Add SRC-INDEX routing or SRC-10 proof coverage.",
                    record,
                )
            )
        if record.id.startswith("PROJECT-SCOPE-") and not _has_inbound_from_prefix(index, record.id, ("TEST-", "DONE-")):
            issues.append(
                issue(
                    "WARNING",
                    "PROJECT_SCOPE_NOT_REFERENCED_BY_TEST_OR_DONE",
                    "Project scope record is not referenced by TEST-* or DONE-* records.",
                    "Project scope should normally be reflected in acceptance proof or DoD.",
                    "no TEST-/DONE- inbound trace",
                    "Add SRC-10 proof/DoD coverage if the scope is intended to be enforceable.",
                    record,
                )
            )
        if record.file == "SRC-10" and record.id.startswith("TEST-") and not record.trace:
            issues.append(
                issue(
                    "WARNING",
                    "SRC10_TEST_WITHOUT_SOURCE_TRACE",
                    "SRC-10 test record has no source requirement trace.",
                    "TEST-* records trace to the source requirements they prove.",
                    "trace=[]",
                    "Add traces to the exact source requirements under test.",
                    record,
                )
            )

    return issues

