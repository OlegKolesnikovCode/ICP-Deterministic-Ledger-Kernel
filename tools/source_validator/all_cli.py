from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from .bld_cli import run_bld_validation
from .cli import run_validation as run_src_validation
from .core.models import ValidationReport, issue
from .core.report import exit_code_for_report
from .outputs.json_report import render_json_report, write_json_report
from .outputs.markdown_report import render_markdown_report, write_markdown_report


def run_all_validation(sources: Path, reports: Path) -> ValidationReport:
    src_report = run_src_validation(sources, reports)
    bld_report = run_bld_validation(sources, reports)
    checked_files = sorted(set(src_report.checked_files) | set(bld_report.checked_files))
    report = ValidationReport(
        checked_files=checked_files,
        checked_records=max(src_report.checked_records, bld_report.checked_records),
        issues=[*src_report.issues, *bld_report.issues],
    )
    reports.mkdir(parents=True, exist_ok=True)
    write_json_report(report, reports / "validation-results.json")
    write_markdown_report(report, reports / "validation-summary.md", "Combined Validation Summary")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRC and BLD governed authority validation.")
    parser.add_argument("--sources", type=Path, default=Path("sources"), help="Source root containing governed JSONL files.")
    parser.add_argument("--reports", type=Path, default=Path("reports"), help="Directory for validation reports.")
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
        report = run_all_validation(args.sources, args.reports)
    except Exception as exc:
        failure = ValidationReport(
            checked_files=[],
            checked_records=0,
            issues=[
                issue(
                    "BLOCKING",
                    "TOOL_FAILURE",
                    "Combined validator failed before completing validation.",
                    "Combined validator completes deterministically and writes reports.",
                    f"{exc}\n{traceback.format_exc()}",
                    "Fix the validator/tooling failure and rerun.",
                )
            ],
        )
        args.reports.mkdir(parents=True, exist_ok=True)
        write_json_report(failure, args.reports / "validation-results.json")
        write_markdown_report(failure, args.reports / "validation-summary.md", "Combined Validation Summary")
        print("Combined validation TOOL_FAILURE. Reports written.")
        return 4

    if args.format == "json":
        print(render_json_report(report))
    elif args.format == "markdown":
        print(render_markdown_report(report, "Combined Validation Summary"))
    else:
        counts = report.counts_by_severity
        print(
            "Combined validation "
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
