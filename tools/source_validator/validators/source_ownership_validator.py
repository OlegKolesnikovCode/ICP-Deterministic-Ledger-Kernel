from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..rules.allowed_tokens import SOURCE_FILE_IDS
from ..rules.source_ownership_rules import (
    IMPLEMENTATION_GUIDANCE_TERMS,
    OWNERSHIP_ASSERTION_TERMS,
    RESPONSIBILITY_MAP,
)


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def validate_source_ownership(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if record.file not in SOURCE_FILE_IDS:
            continue
        statement_text = record.statement.lower()
        text = " ".join([record.statement, record.violation, record.action, record.verification]).lower()

        if _contains_any(statement_text, IMPLEMENTATION_GUIDANCE_TERMS):
            severity = "BLOCKING" if record.file == "SRC-05" else "ERROR"
            issues.append(
                issue(
                    severity,
                    "SOURCE_OWNS_IMPLEMENTATION_GUIDANCE",
                    "SRC record appears to define implementation procedure or implementation paths as source truth.",
                    "SRC files define source requirements, not implementation folder paths, code files, framework workflow, or runtime output.",
                    text[:240],
                    "Move implementation guidance to BLD files later or rewrite this as source-level requirement language.",
                    record,
                )
            )

        if not _contains_any(text, OWNERSHIP_ASSERTION_TERMS):
            continue

        for owner, phrases in RESPONSIBILITY_MAP.items():
            if owner == record.file:
                continue
            matched = [phrase for phrase in phrases if phrase in text]
            if matched:
                issues.append(
                    issue(
                        "WARNING",
                        "SOURCE_RESPONSIBILITY_DRIFT",
                        "SRC record asserts ownership over concepts normally owned by another SRC file.",
                        f"{', '.join(matched)} belongs to {owner}.",
                        f"{record.file} assertion: {record.statement}",
                        "Move the ownership assertion to the responsible file, or rewrite this as a trace/reference statement.",
                        record,
                    )
                )

    return issues
