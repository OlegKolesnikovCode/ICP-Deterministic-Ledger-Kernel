from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..rules.bld_registry import (
    BLD_FILE_IDS,
    BLD_INDEX_FILE,
    CANONICAL_BLD_FAMILIES,
    bld_record_family,
    split_csv,
    statement_key_values,
)

FAMILY_ORDER = {family: index for index, family in enumerate(CANONICAL_BLD_FAMILIES)}


def _expand_family_token(token: str) -> set[str]:
    normalized = token.strip().upper()
    if not normalized:
        return set()
    if normalized == "PIPELINE_OR_STRUCTURE":
        return {"PIPELINE", "STRUCTURE"}
    if normalized == "STATE_OR_DATA":
        return {"STATE", "DATA"}
    if normalized in FAMILY_ORDER:
        return {normalized}
    return set()


def _omission_families(record: Record) -> tuple[set[str], bool]:
    fields = statement_key_values(record.statement)
    omitted: set[str] = set()
    for value in split_csv(fields.get("omitted_families", "")):
        omitted.update(_expand_family_token(value))
    has_justification = bool(fields.get("justification") or fields.get("not_applicable"))
    return omitted, has_justification


def _records_by_bld_file(records: list[Record]) -> dict[str, list[Record]]:
    grouped: dict[str, list[Record]] = {}
    for record in records:
        if record.file.startswith("BLD-"):
            grouped.setdefault(record.file, []).append(record)
    return grouped


def validate_bld_template(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    grouped = _records_by_bld_file(records)

    for file_id, file_records in sorted(grouped.items()):
        if file_id == BLD_INDEX_FILE:
            continue

        present: set[str] = set()
        omitted: set[str] = set()
        sequence: list[tuple[str, Record]] = []

        for record in file_records:
            family = bld_record_family(record.id, file_id)
            if family in FAMILY_ORDER:
                present.add(family)
                sequence.append((family, record))
            if family == "OMISSION" or "omitted_families=" in record.statement:
                record_omissions, has_justification = _omission_families(record)
                if not record_omissions:
                    issues.append(
                        issue(
                            "BLOCKING",
                            "BLD_TEMPLATE_INVALID_OMISSION",
                            "BLD omission record does not name omitted canonical families.",
                            "OMISSION records use omitted_families=<family,...>.",
                            record.statement,
                            "Add omitted_families with canonical BLD family names.",
                            record,
                        )
                    )
                if not has_justification:
                    issues.append(
                        issue(
                            "BLOCKING",
                            "BLD_TEMPLATE_OMISSION_UNJUSTIFIED",
                            "BLD omission record lacks a machine-detectable not-applicable justification.",
                            "OMISSION records include justification= or not_applicable=.",
                            record.statement,
                            "Add a concise machine-detectable justification for the omitted families.",
                            record,
                        )
                    )
                omitted.update(record_omissions)

        missing = [family for family in CANONICAL_BLD_FAMILIES if family not in present and family not in omitted]
        if missing:
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_TEMPLATE_MISSING_FAMILY",
                    "BLD file lacks required canonical record families without explicit omission.",
                    ", ".join(CANONICAL_BLD_FAMILIES),
                    ", ".join(missing),
                    "Add the missing family records or an explicit OMISSION record tied to each omitted family.",
                    file=file_id,
                )
            )

        if file_id in BLD_FILE_IDS and file_id != "BLD-00":
            previous_order = -1
            previous_family = ""
            for family, record in sequence:
                current_order = FAMILY_ORDER[family]
                if current_order < previous_order:
                    issues.append(
                        issue(
                            "BLOCKING",
                            "BLD_TEMPLATE_FAMILY_ORDER",
                            "BLD implementation-control file has canonical families out of order.",
                            "FILE>ROLE>SCOPE>READ>SRC>TARGET>CONTRACT>PIPELINE>STRUCTURE>STATE>DATA>FAILURE>FORBID>TEST>REVIEW>STOP",
                            f"{family} appears after {previous_family}",
                            "Move records so canonical family order is preserved, or justify omitted families explicitly.",
                            record,
                        )
                    )
                    break
                previous_order = current_order
                previous_family = family

    return issues

