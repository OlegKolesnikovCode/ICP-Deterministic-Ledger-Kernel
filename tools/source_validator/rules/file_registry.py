from __future__ import annotations

from .allowed_tokens import GOV_FILE, SOURCE_FILE_IDS, SRC_INDEX_FILE

GOV_FILE_NAME = "GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl"
SRC_INDEX_FILE_NAME = "SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl"

SRC_FILE_NAMES = {
    "SRC-00": "SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl",
    "SRC-01": "SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl",
    "SRC-02": "SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl",
    "SRC-03": "SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl",
    "SRC-04": "SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl",
    "SRC-05": "SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl",
    "SRC-06": "SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl",
    "SRC-07": "SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl",
    "SRC-08": "SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl",
    "SRC-09": "SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl",
    "SRC-10": "SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl",
}

FILE_ID_TO_NAME = {
    GOV_FILE: GOV_FILE_NAME,
    SRC_INDEX_FILE: SRC_INDEX_FILE_NAME,
    **SRC_FILE_NAMES,
}

EXPECTED_FILE_NAMES = [GOV_FILE_NAME, SRC_INDEX_FILE_NAME, *SRC_FILE_NAMES.values()]
EXPECTED_FILE_IDS = tuple(FILE_ID_TO_NAME)

NAME_TO_FILE_ID = {name: file_id for file_id, name in FILE_ID_TO_NAME.items()}

EXPECTED_FILE_CLASS = {
    GOV_FILE: "GOVERNANCE",
    SRC_INDEX_FILE: "INDEX",
    **{file_id: "SOURCE" for file_id in SOURCE_FILE_IDS},
}

EXPECTED_AUTHORITY_LEVEL = {
    GOV_FILE: 0,
    SRC_INDEX_FILE: 1,
    **{file_id: 2 for file_id in SOURCE_FILE_IDS},
}

BLD_FILE_PREFIX = "BLD"


def expected_subdir_for_filename(filename: str) -> str:
    subdirs = expected_subdirs_for_filename(filename)
    return subdirs[0] if subdirs else "."


def expected_subdirs_for_filename(filename: str) -> tuple[str, ...]:
    file_id = NAME_TO_FILE_ID.get(filename, "")
    if file_id == GOV_FILE:
        return ("gov", "GOV")
    if file_id == SRC_INDEX_FILE or file_id.startswith("SRC-"):
        return ("src", "SRC")
    return (".",)


def file_id_from_filename(filename: str) -> str | None:
    return NAME_TO_FILE_ID.get(filename)


def canonical_file_meta_statement(file_id: str) -> str:
    file_class = EXPECTED_FILE_CLASS[file_id]
    authority_level = EXPECTED_AUTHORITY_LEVEL[file_id]
    return (
        f"file_id={file_id};file_class={file_class};authority_level={authority_level};"
        "governed_by=GOV-00;status=ACTIVE"
    )
