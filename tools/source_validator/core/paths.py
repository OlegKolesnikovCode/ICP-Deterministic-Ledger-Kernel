from __future__ import annotations

from pathlib import Path

from .models import ValidationIssue, issue
from ..rules.file_registry import (
    BLD_FILE_PREFIX,
    EXPECTED_FILE_NAMES,
    expected_subdirs_for_filename,
)


def resolve_sources_root(requested: Path) -> tuple[Path, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    if requested.exists():
        return requested, issues

    fallback_candidates = [Path.cwd() / "sources"]
    if requested.name.lower() == "sources":
        fallback_candidates.append(Path.cwd() / "doc")
    fallback_candidates.append(requested.parent / "doc")

    for candidate in fallback_candidates:
        if candidate == requested:
            continue
        if candidate.exists():
            issues.append(
                issue(
                    "INFO",
                    "SOURCE_PATH_FALLBACK",
                    "Requested sources path was not present; validator used the repository doc authority layout.",
                    "A source root containing GOV/SRC governed files.",
                    str(requested),
                    f"Use --sources {candidate} explicitly or create the requested source root.",
                )
            )
            return candidate, issues
    return requested, issues


def expected_paths(source_root: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for filename in EXPECTED_FILE_NAMES:
        candidates = [source_root / filename]
        candidates.extend(source_root / subdir / filename for subdir in expected_subdirs_for_filename(filename))
        paths[filename] = next((candidate for candidate in candidates if candidate.exists()), candidates[-1])
    return paths


def detect_bld_files(source_root: Path) -> list[Path]:
    if not source_root.exists():
        return []
    return sorted(path for path in source_root.rglob("*.jsonl") if path.name.startswith(BLD_FILE_PREFIX))
