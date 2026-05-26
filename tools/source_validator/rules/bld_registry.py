from __future__ import annotations

import re

from .allowed_tokens import GOV_FILE, SOURCE_FILE_IDS, SRC_INDEX_FILE

BLD_INDEX_FILE = "BLD-INDEX"
BLD_FILE_IDS = tuple(f"BLD-{number:02d}" for number in range(0, 11))
BLD_CONTROL_FILE_IDS = (BLD_INDEX_FILE, *BLD_FILE_IDS)

BLD_INDEX_FILE_NAME = "BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl"
BLD_00_FILE_NAME = "BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl"

EXPECTED_BLD_CLASS = {
    BLD_INDEX_FILE: "INDEX",
    **{file_id: "BUILD" for file_id in BLD_FILE_IDS},
}

EXPECTED_BLD_AUTHORITY_LEVEL = {
    BLD_INDEX_FILE: 3,
    **{file_id: 4 for file_id in BLD_FILE_IDS},
}

REQUIRED_BLD_INDEX_RECORD_IDS = (
    "BLD-INDEX-TEMPLATE-001",
    "BLD-INDEX-TEMPLATE-002",
    "BLD-INDEX-TEMPLATE-003",
    "BLD-INDEX-CODEGEN-001",
    "BLD-INDEX-CODEGEN-002",
    "BLD-INDEX-CONTRACT-001",
    "BLD-INDEX-PRECONDITION-010",
    "BLD-INDEX-VALIDATION-012",
    "BLD-INDEX-TRACE-001",
    "BLD-INDEX-STOP-002",
)

CANONICAL_BLD_FAMILIES = (
    "FILE",
    "ROLE",
    "SCOPE",
    "READ",
    "SRC",
    "TARGET",
    "CONTRACT",
    "PIPELINE",
    "STRUCTURE",
    "STATE",
    "DATA",
    "FAILURE",
    "FORBID",
    "TEST",
    "REVIEW",
    "STOP",
)

IMPLEMENTATION_AFFECTING_FAMILIES = {
    "TARGET",
    "CONTRACT",
    "PIPELINE",
    "STRUCTURE",
    "STATE",
    "DATA",
    "FAILURE",
    "FORBID",
    "TEST",
    "REVIEW",
    "STOP",
}

PREFERRED_STATEMENT_TOKENS = {
    "kind",
    "target",
    "responsibility",
    "must",
    "must_not",
    "input",
    "output",
    "allowed_result",
    "forbidden_result",
    "caller",
    "callee",
    "state",
    "pipeline_step",
    "order",
    "failure",
    "proof",
    "test",
    "review",
    "stop_if",
    "source",
    "trace_to",
}

FILE_NAME_ONLY_TRACE_IDS = (GOV_FILE, SRC_INDEX_FILE, *SOURCE_FILE_IDS, *BLD_CONTROL_FILE_IDS)

KEY_VALUE_RE = re.compile(r"(?:^|[;,\s])([A-Za-z][A-Za-z0-9_]*)=")


def bld_file_id_from_filename(filename: str) -> str | None:
    file_id = filename.split("__", 1)[0]
    if file_id in BLD_CONTROL_FILE_IDS:
        return file_id
    return None


def canonical_bld_meta_statement(file_id: str) -> str:
    return (
        f"file_id={file_id};"
        f"file_class={EXPECTED_BLD_CLASS[file_id]};"
        f"authority_level={EXPECTED_BLD_AUTHORITY_LEVEL[file_id]};"
        "governed_by=GOV-00;status=ACTIVE"
    )


def bld_record_family(record_id: str, file_id: str) -> str | None:
    prefix = f"{file_id}-"
    if not record_id.startswith(prefix):
        return None
    suffix = record_id[len(prefix) :]
    if not suffix:
        return None
    first_segment = suffix.split("-", 1)[0]
    if first_segment in CANONICAL_BLD_FAMILIES or first_segment == "OMISSION":
        return first_segment
    return first_segment


def statement_key_values(statement: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for chunk in statement.split(";"):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        key = key.strip()
        if key:
            pairs[key] = value.strip()
    return pairs


def statement_keys(statement: str) -> set[str]:
    return {match.group(1) for match in KEY_VALUE_RE.finditer(statement)}


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]

