from __future__ import annotations

from collections import Counter
from pathlib import Path

from ..core.models import ValidationIssue, ValidationReport


def _escape(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _repair_order(issues: list[ValidationIssue]) -> list[str]:
    categories = []
    seen = set()
    for severity in ("BLOCKING", "ERROR", "WARNING", "INFO"):
        for issue in issues:
            if issue.severity == severity and issue.category not in seen:
                seen.add(issue.category)
                categories.append(f"{severity}: {issue.category}")
    return categories


def render_markdown_report(report: ValidationReport, title: str = "SRC Validation Summary") -> str:
    counts = report.counts_by_severity
    category_counts = Counter(issue.category for issue in report.issues)
    lines = [
        f"# {title}",
        "",
        f"- Verdict: {report.verdict}",
        f"- Files checked: {len(report.checked_files)}",
        f"- Records checked: {report.checked_records}",
        f"- Blocking issues: {counts['BLOCKING']}",
        f"- Errors: {counts['ERROR']}",
        f"- Warnings: {counts['WARNING']}",
        f"- Info: {counts['INFO']}",
        "",
        "## Issue Table",
        "",
        "| Severity | Category | Record | File | Line | Problem | Suggested fix |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not report.issues:
        lines.append("| INFO | NO_ISSUES |  |  |  | No validation issues detected. | No repair required. |")
    else:
        for item in report.issues:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _escape(item.severity),
                        _escape(item.category),
                        _escape(item.record_id),
                        _escape(item.file),
                        _escape(item.line_number),
                        _escape(item.problem),
                        _escape(item.suggested_fix),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Recommended Repair Order", ""])
    order = _repair_order(report.issues)
    if order:
        for item in order:
            count = category_counts[item.split(": ", 1)[1]]
            lines.append(f"- {item} ({count})")
    else:
        lines.append("- No repairs required.")
    lines.append("")
    return "\n".join(lines)


def write_markdown_report(report: ValidationReport, path: Path, title: str = "SRC Validation Summary") -> None:
    path.write_text(render_markdown_report(report, title), encoding="utf-8")
