from __future__ import annotations

import re

from ..core.models import Record

BASE_NAMESPACE_OWNERS = {
    "PROJECT": "SRC-00",
    "ADR": "SRC-00",
    "ARCH": "SRC-01",
    "AUTH": "SRC-01",
    "BOOT": "SRC-01",
    "ENTITY": "SRC-02",
    "ACCOUNT": "SRC-02",
    "ASSET": "SRC-02",
    "BAL": "SRC-02",
    "AMOUNT": "SRC-02",
    "OPER": "SRC-02",
    "LIFE": "SRC-03",
    "TRANSFER": "SRC-03",
    "RESULT": "SRC-03",
    "IDEMP": "SRC-04",
    "LEDGER": "SRC-05",
    "JOURNAL": "SRC-05",
    "TIME": "SRC-05",
    "INV": "SRC-05",
    "FAIL": "SRC-06",
    "READ": "SRC-07",
    "STABLE": "SRC-08",
    "UPG": "SRC-08",
    "API": "SRC-09",
    "FORBID": "SRC-09",
    "TEST": "SRC-10",
    "DONE": "SRC-10",
    "FALSIFIER": "SRC-10",
    "RISK": "SRC-10",
}

NAMESPACE_DECLARATION_RE = re.compile(r"\b([A-Z][A-Z0-9-]*)-\* ids are owned by (SRC-\d{2})\b")


def derive_namespace_owners(records: list[Record]) -> tuple[dict[str, str], dict[str, set[str]]]:
    owners = dict(BASE_NAMESPACE_OWNERS)
    conflicts: dict[str, set[str]] = {}
    for record in records:
        if record.file != "SRC-INDEX":
            continue
        for prefix, owner in NAMESPACE_DECLARATION_RE.findall(record.statement):
            existing = owners.get(prefix)
            if existing and existing != owner:
                conflicts.setdefault(prefix, {existing}).add(owner)
            else:
                owners[prefix] = owner
    return owners, conflicts


def longest_namespace_match(record_id: str, owners: dict[str, str]) -> str | None:
    matches = [prefix for prefix in owners if record_id.startswith(prefix + "-")]
    if not matches:
        return None
    return max(matches, key=len)

