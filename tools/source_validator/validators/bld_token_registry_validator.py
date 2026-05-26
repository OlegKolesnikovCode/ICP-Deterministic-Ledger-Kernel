from __future__ import annotations

import re

from ..core.models import Record, ValidationIssue, issue


def _authorized_values(records: list[Record], record_id: str, key: str) -> set[str]:
    for record in records:
        if record.id != record_id:
            continue
        match = re.search(rf"{re.escape(key)}=\[([^\]]*)\]", record.statement)
        if not match:
            return set()
        return {item.strip() for item in match.group(1).split(",") if item.strip()}
    return set()


def validate_bld_token_registry(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    authorized_types = _authorized_values(records, "GOV-REG-001", "AUTHORIZED_TYPES")
    authorized_classes = _authorized_values(records, "GOV-REG-002", "AUTHORIZED_CLASSES")
    authorized_scopes = _authorized_values(records, "GOV-REG-003", "AUTHORIZED_SCOPES")

    if not (authorized_types and authorized_classes and authorized_scopes):
        issues.append(
            issue(
                "BLOCKING",
                "GOV_REGISTRY_UNAVAILABLE_FOR_BLD",
                "GOV registry records required for BLD token validation are missing or unparsable.",
                "GOV-REG-001, GOV-REG-002, and GOV-REG-003 declare authorized type, class, and scope tokens.",
                "one or more registries unavailable",
                "Restore GOV registry records before validating BLD files.",
                file="GOV-00",
            )
        )
        return issues

    for record in records:
        if not record.file.startswith("BLD-"):
            continue
        if record.type not in authorized_types:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_UNAUTHORIZED_TYPE_TOKEN",
                    "BLD record uses a type token not declared by GOV-00.",
                    ", ".join(sorted(authorized_types)),
                    record.type,
                    "Use a GOV-REG-001 authorized type token or update GOV-00 before using a new token.",
                    record,
                )
            )
        if record.class_name not in authorized_classes:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_UNAUTHORIZED_CLASS_TOKEN",
                    "BLD record uses a class token not declared by GOV-00.",
                    ", ".join(sorted(authorized_classes)),
                    record.class_name,
                    "Use a GOV-REG-002 authorized class token or update GOV-00 before using a new token.",
                    record,
                )
            )
        unknown_scopes = [scope for scope in record.scope if scope not in authorized_scopes]
        if unknown_scopes:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_UNAUTHORIZED_SCOPE_TOKEN",
                    "BLD record uses scope tokens not declared by GOV-00.",
                    ", ".join(sorted(authorized_scopes)),
                    ", ".join(unknown_scopes),
                    "Use GOV-REG-003 authorized scope tokens or update GOV-00 before using new scopes.",
                    record,
                )
            )

    return issues

