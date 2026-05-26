from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue

GUARDRAIL_CUES = (
    "must not",
    "cannot",
    "forbidden",
    "reject",
    "stop",
    "without",
    "lacks",
    "missing",
    "invalid",
    "no_bld_record",
    "blocked_generation",
    "validation_rule=",
)

CONCRETE_IMPLEMENTATION_TERMS = (
    "transfer execution order",
    "ledger commit algorithm",
    "commit algorithm",
    "idempotency storage",
    "service internals",
    "module internals",
    "function body",
    "code path",
    "generated application module",
    "balance map",
    "hashmap",
    "stable btree",
    "stablebtree",
    "debit before credit",
    "credit before debit",
    ".mo",
    ".rs",
    "src/",
    "canister method",
)


def _is_guardrail_statement(record: Record) -> bool:
    text = " ".join([record.type, record.statement, record.action]).lower()
    return record.type in {"MUST_NOT", "FORBIDS"} or any(cue in text for cue in GUARDRAIL_CUES)


def _matched_concrete_terms(record: Record) -> list[str]:
    lowered = record.statement.lower()
    return [term for term in CONCRETE_IMPLEMENTATION_TERMS if term in lowered]


def validate_bld_guardrails(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if record.file not in {"BLD-INDEX", "BLD-00"}:
            continue
        matched = _matched_concrete_terms(record)
        if not matched or _is_guardrail_statement(record):
            continue
        if record.file == "BLD-INDEX":
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_INDEX_IMPLEMENTATION_DETAIL",
                    "BLD-INDEX appears to define concrete implementation behavior instead of routing/enforcement.",
                    "BLD-INDEX remains procedural: routing, classification, lookup, validation, conflict escalation, and generation order only.",
                    ", ".join(matched),
                    "Move concrete implementation behavior to the authorized BLD-01 through BLD-10 file or remove it.",
                    record,
                )
            )
        else:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_00_IMPLEMENTATION_DETAIL",
                    "BLD-00 appears to define detailed implementation behavior instead of global implementation identity guidance.",
                    "BLD-00 remains limited to implementation identity, project scope, non-goals, and project-level ADR framing.",
                    ", ".join(matched),
                    "Move detailed implementation behavior to the authorized BLD-01 through BLD-10 file or remove it.",
                    record,
                )
            )

    return issues

