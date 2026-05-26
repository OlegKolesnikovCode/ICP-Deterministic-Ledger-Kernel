from __future__ import annotations

from pathlib import Path

from ..core.models import ValidationIssue, ValidationReport


RULE_HINTS = {
    "JSONL_SYNTAX": "schema_validator.py: each non-empty line must be exactly one JSON object.",
    "SCHEMA_MISSING_FIELD": "schema_validator.py: fixed GOV-00 field set is mandatory.",
    "SCHEMA_EXTRA_FIELD": "schema_validator.py: no undeclared fields.",
    "SCHEMA_FIELD_ORDER": "schema_validator.py: canonical field order is mandatory.",
    "SCHEMA_WRONG_TYPE": "schema_validator.py: primitive field types are fixed.",
    "DUPLICATE_RECORD_ID": "record_index.py: governed record ids are globally unique.",
    "TRACE_UNRESOLVED": "trace_resolution_validator.py: trace ids must resolve to loaded GOV/SRC records.",
    "TRACE_TO_BLD": "trace_resolution_validator.py: SRC-only mode forbids BLD traces.",
    "TRACE_DIRECTION_TO_BLD": "trace_direction_validator.py: source authority cannot depend on BLD authority.",
    "NAMESPACE_OWNER_MISMATCH": "namespace_ownership_validator.py: prefixes must be defined only in owning SRC files.",
    "SRC10_CREATES_SOURCE_TRUTH": "src10_usage_validator.py: SRC-10 cannot create primary source truth.",
    "SRC10_SCOPE_LEAKAGE": "src10_usage_validator.py: SRC-10 proof/risk records cannot support scope directly.",
}


def _format_issue(item: ValidationIssue) -> list[str]:
    return [
        f"- Record: {item.record_id or '(file-level)'}",
        f"  File: {item.file or '(unknown)'}",
        f"  Line: {item.line_number or '(unknown)'}",
        f"  Severity: {item.severity}",
        f"  Category: {item.category}",
        f"  Problem: {item.problem}",
        f"  Expected: {item.expected}",
        f"  Actual: {item.actual}",
        f"  Controlling rule: {RULE_HINTS.get(item.category, 'See validator category and governed rule traces.')}",
        f"  Suggested fix: {item.suggested_fix}",
    ]


def render_codex_prompt(report: ValidationReport) -> str:
    failed = [issue for issue in report.issues if issue.severity in {"BLOCKING", "ERROR"}]
    lines = [
        "# Codex SRC Repair Prompt",
        "",
        "You are repairing governed GOV/SRC JSONL source authority files after deterministic SRC-only validation.",
        "",
        "Do not change BLD files. Do not create BLD validators. Do not infer new GOV/SRC rules.",
        "Stop after the listed BLOCKING and ERROR issues are resolved and rerun the SRC validator.",
        "",
        f"Verdict: {report.verdict}",
        f"Blocking/Error issue count: {len(failed)}",
        "",
        "## Failed Records",
        "",
    ]
    if not failed:
        lines.append("No BLOCKING or ERROR issues were detected. Review WARNING items only if desired.")
    else:
        for item in failed:
            lines.extend(_format_issue(item))
            lines.append("")

    likely_files = sorted({issue.file for issue in failed if issue.file})
    lines.extend(["", "## Files Likely Needing Edits", ""])
    if likely_files:
        lines.extend(f"- {file_id}" for file_id in likely_files)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Stop Conditions",
            "",
            "- Stop if a suggested fix would require creating or validating BLD files.",
            "- Stop if fixing an issue requires changing project semantics rather than correcting structure, trace, namespace, or ownership mechanics.",
            "- Stop after deterministic validation reaches PASS or WARNING_ONLY for the targeted fix set.",
            "",
            "## Do-Not-Change Warnings",
            "",
            "- Do not modify implementation app code.",
            "- Do not use README, runtime behavior, tests, generated output, or chat history as source authority.",
            "- Do not broaden SRC-10 from proof/risk/DoD authority into domain/source authority.",
        ]
    )
    return "\n".join(lines)


def write_codex_prompt(report: ValidationReport, path: Path) -> None:
    path.write_text(render_codex_prompt(report), encoding="utf-8")
