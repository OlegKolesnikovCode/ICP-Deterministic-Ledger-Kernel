from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Record:
    id: str
    file: str
    class_name: str
    type: str
    scope: list[str]
    authority_level: int
    statement: str
    violation: str
    action: str
    verification: str
    trace: list[str]
    source_path: Path
    line_number: int

    @classmethod
    def from_mapping(
        cls,
        raw: dict[str, Any],
        source_path: Path,
        line_number: int,
    ) -> "Record":
        return cls(
            id=raw["id"],
            file=raw["file"],
            class_name=raw["class"],
            type=raw["type"],
            scope=list(raw["scope"]),
            authority_level=raw["authority_level"],
            statement=raw["statement"],
            violation=raw["violation"],
            action=raw["action"],
            verification=raw["verification"],
            trace=list(raw["trace"]),
            source_path=source_path,
            line_number=line_number,
        )


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    category: str
    record_id: str | None
    file: str | None
    line_number: int | None
    problem: str
    expected: str
    actual: str
    suggested_fix: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "record_id": self.record_id,
            "file": self.file,
            "line_number": self.line_number,
            "problem": self.problem,
            "expected": self.expected,
            "actual": self.actual,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class ValidationReport:
    checked_files: list[str]
    checked_records: int
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def counts_by_severity(self) -> dict[str, int]:
        counts = {"BLOCKING": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

    @property
    def verdict(self) -> str:
        counts = self.counts_by_severity
        if counts["BLOCKING"] or counts["ERROR"]:
            return "FAIL"
        if counts["WARNING"]:
            return "WARNING_ONLY"
        return "PASS"

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "WARNING"]

    @property
    def infos(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "INFO"]

    def to_dict(self) -> dict[str, Any]:
        counts = self.counts_by_severity
        return {
            "verdict": self.verdict,
            "checked_files": self.checked_files,
            "checked_records": self.checked_records,
            "counts": {
                "blocking": counts["BLOCKING"],
                "errors": counts["ERROR"],
                "warnings": counts["WARNING"],
                "info": counts["INFO"],
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }


def issue(
    severity: str,
    category: str,
    problem: str,
    expected: str,
    actual: str,
    suggested_fix: str,
    record: Record | None = None,
    file: str | None = None,
    line_number: int | None = None,
    record_id: str | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        category=category,
        record_id=record.id if record else record_id,
        file=record.file if record else file,
        line_number=record.line_number if record else line_number,
        problem=problem,
        expected=expected,
        actual=actual,
        suggested_fix=suggested_fix,
    )

