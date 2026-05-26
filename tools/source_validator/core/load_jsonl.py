from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


class DuplicateKeyError(ValueError):
    pass


def _ordered_no_duplicates(pairs: list[tuple[str, Any]]) -> OrderedDict[str, Any]:
    seen: set[str] = set()
    ordered: OrderedDict[str, Any] = OrderedDict()
    for key, value in pairs:
        if key in seen:
            raise DuplicateKeyError(f"duplicate key: {key}")
        seen.add(key)
        ordered[key] = value
    return ordered


def parse_json_object(line: str) -> OrderedDict[str, Any]:
    value = json.loads(line, object_pairs_hook=_ordered_no_duplicates)
    if not isinstance(value, OrderedDict):
        raise TypeError(f"expected JSON object, got {type(value).__name__}")
    return value


def iter_jsonl_lines(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if stripped:
                yield line_number, stripped

