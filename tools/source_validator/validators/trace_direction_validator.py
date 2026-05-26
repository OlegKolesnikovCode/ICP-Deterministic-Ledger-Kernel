from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..core.record_index import RecordIndex
from ..rules.trace_direction_rules import PROOF_USAGE_TERMS, SOURCE_AUTHORITY_FORBIDDEN_SUPPORT_TERMS

AUTHORITY_SUPPORT_TERMS = [
    "based on",
    "derived from",
    "inferred from",
    "justified by",
    "supported by",
    "as authority",
    "source truth",
]


def _has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def validate_trace_direction(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        combined_text = " ".join([record.statement, record.violation, record.action, record.verification]).lower()
        statement_text = record.statement.lower()
        if (
            record.file.startswith("SRC-")
            and _has_any(statement_text, SOURCE_AUTHORITY_FORBIDDEN_SUPPORT_TERMS)
            and _has_any(statement_text, AUTHORITY_SUPPORT_TERMS)
            and "must not" not in statement_text
            and "forbid" not in statement_text
        ):
            issues.append(
                issue(
                    "ERROR",
                    "SOURCE_AUTHORITY_INVERSION",
                    "SRC record appears to cite implementation, README, test output, runtime output, or chat history as authority.",
                    "SRC authority is supported by governed GOV/SRC records only.",
                    combined_text[:240],
                    "Rewrite the source claim to trace to governed source authority; move implementation evidence to BLD validation later.",
                    record,
                )
            )

        for trace_id in record.trace:
            if trace_id.startswith("BLD-"):
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_DIRECTION_TO_BLD",
                        "SRC-layer trace points from source authority to BLD authority.",
                        "SRC files may trace to GOV, SRC-INDEX, and SRC records only.",
                        trace_id,
                        "Remove BLD traces from GOV/SRC files.",
                        record,
                    )
                )
                continue
            target = index.record_by_id.get(trace_id)
            if not target:
                continue
            if record.file.startswith("SRC-") and target.file.startswith("BLD-"):
                issues.append(
                    issue(
                        "BLOCKING",
                        "TRACE_DIRECTION_TO_BLD",
                        "SRC-layer trace resolves to a BLD record.",
                        "SRC files may trace to GOV, SRC-INDEX, and SRC records only.",
                        f"{trace_id} in {target.file}",
                        "Remove BLD authority from SRC traces.",
                        record,
                    )
                )
            if record.file not in ("SRC-10", "SRC-INDEX") and target.file == "SRC-10":
                if not _has_any(combined_text, PROOF_USAGE_TERMS):
                    issues.append(
                        issue(
                            "ERROR",
                            "SRC10_USED_AS_DOMAIN_AUTHORITY",
                            "Non-SRC-10 source record traces to SRC-10 without proof/risk/verification usage context.",
                            "SRC-10 supports proof, risk, falsifier, and Definition of Done usage only.",
                            trace_id,
                            "Trace domain claims to their owning SRC requirement; keep SRC-10 traces for proof/risk context only.",
                            record,
                        )
                    )

    return issues
