from __future__ import annotations

import json
from pathlib import Path

from ..core.models import ValidationReport


def write_json_report(report: ValidationReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=False) + "\n", encoding="utf-8")


def render_json_report(report: ValidationReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=False)

