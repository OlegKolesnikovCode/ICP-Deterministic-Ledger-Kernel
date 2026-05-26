from __future__ import annotations

import re

from ..core.models import Record, ValidationIssue, issue
from ..rules.allowed_tokens import SOURCE_FILE_IDS
from ..rules.source_ownership_rules import RESPONSIBILITY_MAP

INDEX_ROUTING_TERMS = [
    "route",
    "routing",
    "index",
    "lookup",
    "reference",
    "trace",
    "traceability",
    "namespace",
    "classification",
    "validation",
    "escalation",
    "generation order",
    "owns",
    "owned by",
    "input",
]

IMPLEMENTATION_TERMS = [
    "code file",
    "framework",
    "write implementation",
    "implementation folder",
]


def _has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def validate_src_index(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    index_records = [record for record in records if record.file == "SRC-INDEX"]
    mentioned_source_files: set[str] = set()

    for record in index_records:
        statement_text = record.statement.lower()
        text = " ".join([record.statement, record.violation, record.action, record.verification]).lower()
        mentioned_source_files.update(re.findall(r"\bSRC-\d{2}\b", record.statement))

        if _has_any(statement_text, IMPLEMENTATION_TERMS):
            issues.append(
                issue(
                    "BLOCKING",
                    "SRC_INDEX_IMPLEMENTATION_GUIDANCE",
                    "SRC-INDEX record creates implementation guidance.",
                    "SRC-INDEX routes, indexes, maps, validates, and escalates SRC authority only.",
                    record.statement,
                    "Move implementation guidance out of SRC-INDEX and into later BLD authority if governed.",
                    record,
                )
            )

        if not _has_any(text, INDEX_ROUTING_TERMS):
            issues.append(
                issue(
                    "WARNING",
                    "SRC_INDEX_NON_ROUTING_LANGUAGE",
                    "SRC-INDEX record does not clearly read as routing, lookup, namespace, validation, or escalation authority.",
                    "SRC-INDEX should not redefine source truth.",
                    record.statement,
                    "Rewrite as routing/index authority or move source truth to the owning SRC file.",
                    record,
                )
            )

        if record.id.startswith("SRC-INDEX-RESPONSIBILITY"):
            owner_match = re.search(r"\b(SRC-\d{2}) owns\b", record.statement)
            if owner_match:
                owner = owner_match.group(1)
                if owner not in RESPONSIBILITY_MAP:
                    issues.append(
                        issue(
                            "BLOCKING",
                            "SRC_INDEX_UNKNOWN_RESPONSIBILITY_OWNER",
                            "SRC-INDEX responsibility record assigns ownership to an unknown SRC file.",
                            "Responsibility owner is SRC-00 through SRC-10.",
                            owner,
                            "Correct responsibility routing to an active SRC file.",
                            record,
                        )
                    )
                elif owner not in record.scope:
                    issues.append(
                        issue(
                            "ERROR",
                            "SRC_INDEX_RESPONSIBILITY_SCOPE_MISMATCH",
                            "SRC-INDEX responsibility record does not include the owning SRC file in scope.",
                            f"scope includes {owner}.",
                            str(record.scope),
                            "Add the owning SRC file to the responsibility record scope.",
                            record,
                        )
                    )

    missing_mentions = set(SOURCE_FILE_IDS) - mentioned_source_files
    for missing in sorted(missing_mentions):
        issues.append(
            issue(
                "BLOCKING",
                "SRC_INDEX_MISSING_ACTIVE_SRC_REFERENCE",
                "SRC-INDEX does not reference an active SRC file from the expected registry.",
                "SRC-INDEX references SRC-00 through SRC-10.",
                missing,
                "Add routing/responsibility/namespace reference for the missing SRC file.",
                file="SRC-INDEX",
            )
        )

    return issues
