from __future__ import annotations

from .models import ValidationReport


def exit_code_for_report(report: ValidationReport, fail_on: str = "errors") -> int:
    counts = report.counts_by_severity
    if counts["BLOCKING"]:
        return 3
    if counts["ERROR"]:
        return 2
    if counts["WARNING"] and fail_on == "warnings":
        return 1
    if counts["WARNING"] and fail_on != "warnings":
        return 1
    return 0

