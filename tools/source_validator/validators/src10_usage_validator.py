from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..core.record_index import RecordIndex
from ..rules.src10_rules import SRC10_PREFIX_USAGE, SRC10_PROOF_CONTEXT_TERMS, SRC10_SOURCE_TRUTH_TERMS


def _has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _src10_prefix(record_id: str) -> str | None:
    for prefix in SRC10_PREFIX_USAGE:
        if record_id.startswith(prefix + "-"):
            return prefix
    return None


def validate_src10_usage(records: list[Record], index: RecordIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        text = " ".join([record.statement, record.violation, record.action, record.verification]).lower()
        if record.file == "SRC-10":
            prefix = _src10_prefix(record.id)
            if prefix and not _has_any(text, SRC10_PREFIX_USAGE[prefix]):
                issues.append(
                    issue(
                        "WARNING",
                        "SRC10_PREFIX_USAGE_AMBIGUOUS",
                        "SRC-10 record prefix usage is not clearly constrained to its proof/risk/DoD role.",
                        f"{prefix}-* records use language related to {', '.join(SRC10_PREFIX_USAGE[prefix])}.",
                        record.statement,
                        "Clarify the record as test/proof, Definition of Done, falsifier, or risk authority.",
                        record,
                    )
                )
            statement_text = record.statement.lower()
            if (
                _has_any(statement_text, SRC10_SOURCE_TRUTH_TERMS)
                and not _has_any(statement_text, SRC10_PROOF_CONTEXT_TERMS)
                and " not " not in statement_text
                and "must not" not in statement_text
                and "forbid" not in statement_text
            ):
                issues.append(
                    issue(
                        "BLOCKING",
                        "SRC10_CREATES_SOURCE_TRUTH",
                        "SRC-10 record appears to define source/domain/runtime truth rather than proof requirements.",
                        "SRC-10 owns proof requirements, acceptance criteria, falsifiers, risks, and Definition of Done only.",
                        record.statement,
                        "Move source truth to the owning SRC file and make SRC-10 trace to it as proof/risk coverage.",
                        record,
                    )
                )
        elif record.file.startswith("SRC-"):
            traced_src10 = [trace_id for trace_id in record.trace if index.record_by_id.get(trace_id, None) and index.record_by_id[trace_id].file == "SRC-10"]
            if not traced_src10:
                continue
            if record.file == "SRC-00" and ("project scope" in text or "scope" in text) and not _has_any(text, SRC10_PROOF_CONTEXT_TERMS):
                issues.append(
                    issue(
                        "ERROR",
                        "SRC10_SCOPE_LEAKAGE",
                        "SRC-00 uses SRC-10 proof/risk records as support for project scope without proof-only context.",
                        "Project scope is sourced from SRC-00/GOV authority; SRC-10 can support proof/risk coverage only.",
                        ", ".join(traced_src10),
                        "Trace scope claims to GOV/SRC source authority and keep SRC-10 traces only on proof/risk records.",
                        record,
                    )
                )
            elif not _has_any(text, SRC10_PROOF_CONTEXT_TERMS):
                issues.append(
                    issue(
                        "WARNING",
                        "SRC10_TRACE_CONTEXT_AMBIGUOUS",
                        "SRC record traces to SRC-10 without clear proof/risk/verification context.",
                        "SRC-10 is not generic source authority.",
                        ", ".join(traced_src10),
                        "Clarify that the SRC-10 trace is proof/risk/DoD context or replace it with owning source authority.",
                        record,
                    )
                )

    return issues
