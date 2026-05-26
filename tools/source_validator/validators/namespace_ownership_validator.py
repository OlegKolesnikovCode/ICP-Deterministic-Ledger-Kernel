from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..rules.allowed_tokens import SOURCE_FILE_IDS
from ..rules.namespace_registry import derive_namespace_owners, longest_namespace_match


def validate_namespace_ownership(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    owners, conflicts = derive_namespace_owners(records)

    for prefix, prefix_owners in conflicts.items():
        issues.append(
            issue(
                "BLOCKING",
                "NAMESPACE_MULTI_OWNER",
                "Namespace prefix has conflicting owner declarations.",
                "Each namespace prefix has exactly one owning SRC file.",
                f"{prefix}: {', '.join(sorted(prefix_owners))}",
                "Resolve SRC-INDEX namespace routing to one owner.",
                file="SRC-INDEX",
            )
        )

    for record in records:
        if record.file not in SOURCE_FILE_IDS:
            continue
        prefix = longest_namespace_match(record.id, owners)
        if not prefix:
            if record.id.startswith("GOV-") or record.id.startswith("SRC-INDEX-"):
                continue
            issues.append(
                issue(
                    "BLOCKING",
                    "UNKNOWN_SOURCE_NAMESPACE",
                    "SRC record id uses an unknown namespace prefix.",
                    "SRC record ids use prefixes owned by SRC-INDEX namespace routing.",
                    record.id,
                    "Add an explicit SRC-INDEX namespace declaration or rename the record to an owned prefix.",
                    record,
                )
            )
            continue
        expected_owner = owners[prefix]
        if record.file != expected_owner:
            issues.append(
                issue(
                    "BLOCKING",
                    "NAMESPACE_OWNER_MISMATCH",
                    "Record id prefix is defined in a non-owning SRC file.",
                    f"{prefix}-* records belong in {expected_owner}.",
                    f"{record.id} defined in {record.file}",
                    "Move the record to the owning SRC file or rename it to this file's owned namespace.",
                    record,
                )
            )

    return issues

