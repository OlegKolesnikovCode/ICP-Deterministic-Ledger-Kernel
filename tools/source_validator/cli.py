from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from .core.models import ValidationIssue, ValidationReport, issue
from .core.paths import detect_bld_files, expected_paths, resolve_sources_root
from .core.record_index import build_record_index
from .core.report import exit_code_for_report
from .outputs.codex_prompt_report import write_codex_prompt
from .outputs.json_report import render_json_report, write_json_report
from .outputs.markdown_report import render_markdown_report, write_markdown_report
from .validators.file_manifest_validator import validate_file_manifest
from .validators.namespace_ownership_validator import validate_namespace_ownership
from .validators.schema_validator import validate_jsonl_schema
from .validators.source_ownership_validator import validate_source_ownership
from .validators.src10_usage_validator import validate_src10_usage
from .validators.src_coverage_validator import validate_src_coverage
from .validators.src_index_validator import validate_src_index
from .validators.trace_direction_validator import validate_trace_direction
from .validators.trace_resolution_validator import validate_trace_resolution


def run_validation(sources: Path, reports: Path) -> ValidationReport:
    source_root, path_issues = resolve_sources_root(sources)
    issues: list[ValidationIssue] = list(path_issues)
    paths = expected_paths(source_root)

    bld_files = detect_bld_files(source_root)
    if bld_files:
        issues.append(
            issue(
                "INFO",
                "BLD_FILES_IGNORED",
                "BLD files detected but ignored by SRC-only validator.",
                "Only GOV-00, SRC-INDEX, and SRC-00 through SRC-10 are validated in this phase.",
                ", ".join(str(path) for path in bld_files),
                "Run BLD validation only in a later governed phase.",
            )
        )

    records = []
    checked_files = []
    for filename, path in paths.items():
        if not path.exists():
            continue
        checked_files.append(str(path))
        parsed, schema_issues = validate_jsonl_schema(path)
        records.extend(parsed)
        issues.extend(schema_issues)

    issues.extend(validate_file_manifest(paths, records))
    index = build_record_index(records)
    issues.extend(index.issues)
    issues.extend(validate_trace_resolution(records, index))
    issues.extend(validate_namespace_ownership(records))
    issues.extend(validate_trace_direction(records, index))
    issues.extend(validate_source_ownership(records))
    issues.extend(validate_src_index(records))
    issues.extend(validate_src10_usage(records, index))
    issues.extend(validate_src_coverage(records, index))

    report = ValidationReport(
        checked_files=checked_files,
        checked_records=len(records),
        issues=issues,
    )

    reports.mkdir(parents=True, exist_ok=True)
    write_json_report(report, reports / "src-validation-results.json")
    write_markdown_report(report, reports / "src-validation-summary.md")
    write_codex_prompt(report, reports / "src-codex-repair-prompt.md")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate GOV/SRC source authority files only.")
    parser.add_argument("--sources", type=Path, default=Path("sources"), help="Source root containing GOV/SRC JSONL files.")
    parser.add_argument("--reports", type=Path, default=Path("reports"), help="Directory for JSON/Markdown repair reports.")
    parser.add_argument(
        "--fail-on",
        choices=["warnings", "errors", "blocking"],
        default="errors",
        help="Threshold label retained for CLI compatibility; exit codes still report warning/error/blocking outcomes.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Stdout format. Reports are always written to the reports directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_validation(args.sources, args.reports)
    except Exception as exc:
        failure = ValidationReport(
            checked_files=[],
            checked_records=0,
            issues=[
                issue(
                    "BLOCKING",
                    "TOOL_FAILURE",
                    "SRC validator failed before completing validation.",
                    "Validator completes deterministically and writes reports.",
                    f"{exc}\n{traceback.format_exc()}",
                    "Fix the validator/tooling failure and rerun.",
                )
            ],
        )
        args.reports.mkdir(parents=True, exist_ok=True)
        write_json_report(failure, args.reports / "src-validation-results.json")
        write_markdown_report(failure, args.reports / "src-validation-summary.md")
        write_codex_prompt(failure, args.reports / "src-codex-repair-prompt.md")
        print("SRC validation TOOL_FAILURE. Reports written.")
        return 4

    if args.format == "json":
        print(render_json_report(report))
    elif args.format == "markdown":
        print(render_markdown_report(report))
    else:
        counts = report.counts_by_severity
        print(
            "SRC validation "
            f"{report.verdict}: "
            f"{len(report.checked_files)} files, "
            f"{report.checked_records} records, "
            f"{counts['BLOCKING']} blocking, "
            f"{counts['ERROR']} errors, "
            f"{counts['WARNING']} warnings, "
            f"{counts['INFO']} info."
        )
        print(f"Reports written to {args.reports}")
    return exit_code_for_report(report, args.fail_on)

