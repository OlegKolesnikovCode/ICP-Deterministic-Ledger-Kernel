from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from .core.models import ValidationIssue, ValidationReport, issue
from .core.paths import detect_bld_files, expected_paths, resolve_sources_root
from .core.record_index import build_record_index
from .core.report import exit_code_for_report
from .outputs.json_report import render_json_report, write_json_report
from .outputs.markdown_report import render_markdown_report, write_markdown_report
from .validators.bld_file_manifest_validator import validate_bld_file_manifest
from .validators.bld_guardrail_validator import validate_bld_guardrails
from .validators.bld_statement_grammar_validator import validate_bld_statement_grammar
from .validators.bld_template_validator import validate_bld_template
from .validators.bld_token_registry_validator import validate_bld_token_registry
from .validators.bld_trace_validator import (
    validate_bld_target_traces,
    validate_bld_trace_direction,
    validate_bld_trace_resolution,
)
from .validators.schema_validator import validate_jsonl_schema


def _all_authority_paths(source_root: Path, bld_files: list[Path]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for path in expected_paths(source_root).values():
        if path.exists() and path not in seen:
            paths.append(path)
            seen.add(path)
    for path in bld_files:
        if path.exists() and path not in seen:
            paths.append(path)
            seen.add(path)
    return paths


def run_bld_validation(sources: Path, reports: Path) -> ValidationReport:
    source_root, path_issues = resolve_sources_root(sources)
    issues: list[ValidationIssue] = list(path_issues)
    bld_files = detect_bld_files(source_root)

    records = []
    checked_files = []
    for path in _all_authority_paths(source_root, bld_files):
        checked_files.append(str(path))
        parsed, schema_issues = validate_jsonl_schema(path)
        records.extend(parsed)
        issues.extend(schema_issues)

    index = build_record_index(records)
    issues.extend(index.issues)
    issues.extend(validate_bld_file_manifest(bld_files, records, set(index.record_by_id)))
    issues.extend(validate_bld_token_registry(records))
    issues.extend(validate_bld_trace_resolution(records, index))
    issues.extend(validate_bld_trace_direction(records, index))
    issues.extend(validate_bld_template(records))
    issues.extend(validate_bld_statement_grammar(records))
    issues.extend(validate_bld_target_traces(records, index))
    issues.extend(validate_bld_guardrails(records))

    report = ValidationReport(
        checked_files=checked_files,
        checked_records=len(records),
        issues=issues,
    )

    reports.mkdir(parents=True, exist_ok=True)
    write_json_report(report, reports / "bld-validation-results.json")
    write_markdown_report(report, reports / "bld-validation-summary.md", "BLD Validation Summary")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate GOV/SRC/BLD authority files for governed BLD generation.")
    parser.add_argument("--sources", type=Path, default=Path("sources"), help="Source root containing GOV/SRC/BLD JSONL files.")
    parser.add_argument("--reports", type=Path, default=Path("reports"), help="Directory for JSON/Markdown validation reports.")
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
        report = run_bld_validation(args.sources, args.reports)
    except Exception as exc:
        failure = ValidationReport(
            checked_files=[],
            checked_records=0,
            issues=[
                issue(
                    "BLOCKING",
                    "TOOL_FAILURE",
                    "BLD validator failed before completing validation.",
                    "Validator completes deterministically and writes reports.",
                    f"{exc}\n{traceback.format_exc()}",
                    "Fix the validator/tooling failure and rerun.",
                )
            ],
        )
        args.reports.mkdir(parents=True, exist_ok=True)
        write_json_report(failure, args.reports / "bld-validation-results.json")
        write_markdown_report(failure, args.reports / "bld-validation-summary.md", "BLD Validation Summary")
        print("BLD validation TOOL_FAILURE. Reports written.")
        return 4

    if args.format == "json":
        print(render_json_report(report))
    elif args.format == "markdown":
        print(render_markdown_report(report, "BLD Validation Summary"))
    else:
        counts = report.counts_by_severity
        print(
            "BLD validation "
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
