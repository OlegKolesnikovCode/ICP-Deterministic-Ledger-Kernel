from __future__ import annotations

from ..core.models import Record, ValidationIssue, issue
from ..rules.bld_registry import (
    IMPLEMENTATION_AFFECTING_FAMILIES,
    PREFERRED_STATEMENT_TOKENS,
    bld_record_family,
    statement_keys,
)


def _has_any_key(keys: set[str], candidates: set[str]) -> bool:
    return bool(keys & candidates)


def _has_stop_equivalent(statement: str) -> bool:
    lowered = statement.lower()
    return "must stop" in lowered or "stop downstream" in lowered or "blocked_until" in lowered


def validate_bld_statement_grammar(records: list[Record]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        if not record.file.startswith("BLD-") or record.file == "BLD-INDEX":
            continue
        family = bld_record_family(record.id, record.file)
        if family not in IMPLEMENTATION_AFFECTING_FAMILIES:
            continue

        keys = statement_keys(record.statement)
        has_preferred_token = _has_any_key(keys, PREFERRED_STATEMENT_TOKENS)
        if not has_preferred_token and not (family == "STOP" and _has_stop_equivalent(record.statement)):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_STATEMENT_MISSING_KEY_VALUE_TOKEN",
                    "Implementation-affecting BLD statement lacks semi-structured key=value grammar.",
                    "At least one preferred BLD key=value token is present where practical.",
                    record.statement,
                    "Rewrite the statement with preferred key=value tokens or move prose to non-implementation guidance.",
                    record,
                )
            )

        if family == "TARGET":
            if "target" not in keys:
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_TARGET_MISSING_TARGET_TOKEN",
                        "TARGET record lacks target= token.",
                        "TARGET records include target=.",
                        record.statement,
                        "Add target=<implementation object> to the TARGET statement.",
                        record,
                    )
                )
            if not _has_any_key(keys, {"responsibility", "must", "must_not"}):
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_TARGET_MISSING_RESPONSIBILITY_TOKEN",
                        "TARGET record lacks responsibility= or equivalent implementation responsibility token.",
                        "TARGET records include responsibility=, must=, or must_not=.",
                        record.statement,
                        "Add responsibility=<owned behavior> or an equivalent must=/must_not= token.",
                        record,
                    )
                )
        elif family == "CONTRACT":
            if "target" not in keys:
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_CONTRACT_MISSING_TARGET_TOKEN",
                        "CONTRACT record lacks target= token.",
                        "CONTRACT records include target=.",
                        record.statement,
                        "Add target=<contracted object> to the CONTRACT statement.",
                        record,
                    )
                )
            if not _has_any_key(keys, {"input", "output"}):
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_CONTRACT_MISSING_IO_TOKEN",
                        "CONTRACT record lacks input= or output= token.",
                        "CONTRACT records include at least one input= or output= token.",
                        record.statement,
                        "Add input=<inputs> or output=<outputs> to the CONTRACT statement.",
                        record,
                    )
                )
        elif family == "PIPELINE" and not _has_any_key(keys, {"order", "pipeline_step", "step"}):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_PIPELINE_MISSING_ORDER_TOKEN",
                    "PIPELINE record lacks order=, pipeline_step=, or step= token.",
                    "PIPELINE records define deterministic order or step identity.",
                    record.statement,
                    "Add order=, pipeline_step=, or step= to the PIPELINE statement.",
                    record,
                )
            )
        elif family == "FORBID" and not _has_any_key(keys, {"must_not", "forbidden_result"}):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_FORBID_MISSING_PROHIBITION_TOKEN",
                    "FORBID record lacks must_not= or forbidden_result= token.",
                    "FORBID records define explicit prohibition or forbidden result.",
                    record.statement,
                    "Add must_not=<forbidden behavior> or forbidden_result=<result>.",
                    record,
                )
            )
        elif family == "FAILURE":
            if not _has_any_key(keys, {"failure", "condition"}):
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_FAILURE_MISSING_CONDITION_TOKEN",
                        "FAILURE record lacks failure= or condition= token.",
                        "FAILURE records identify the invalid or failure condition.",
                        record.statement,
                        "Add failure=<class> or condition=<trigger>.",
                        record,
                    )
                )
            if not _has_any_key(keys, {"must", "allowed_result", "forbidden_result", "result", "behavior"}):
                issues.append(
                    issue(
                        "BLOCKING",
                        "BLD_FAILURE_MISSING_BEHAVIOR_TOKEN",
                        "FAILURE record lacks required deterministic behavior/result token.",
                        "FAILURE records define required behavior or result for the condition.",
                        record.statement,
                        "Add must=, allowed_result=, forbidden_result=, result=, or behavior=.",
                        record,
                    )
                )
        elif family in {"TEST", "REVIEW"} and not _has_any_key(keys, {"proof", "test", "review"}):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_PROOF_MAPPING_MISSING_TOKEN",
                    f"{family} record lacks proof=, test=, or review= token.",
                    "TEST/REVIEW records include source-grounded proof, test, or review mapping.",
                    record.statement,
                    "Add proof=, test=, or review= to the statement.",
                    record,
                )
            )
        elif family == "STOP" and "stop_if" not in keys and not _has_stop_equivalent(record.statement):
            issues.append(
                issue(
                    "BLOCKING",
                    "BLD_STOP_MISSING_STOP_IF_TOKEN",
                    "STOP record lacks stop_if= or equivalent stop condition.",
                    "STOP records include stop_if= or a direct must-stop condition.",
                    record.statement,
                    "Add stop_if=<condition> or rewrite as an explicit must-stop condition.",
                    record,
                )
            )

    return issues

