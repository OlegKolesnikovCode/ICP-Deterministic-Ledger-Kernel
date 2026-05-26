from pathlib import Path

from source_validator.core.models import Record


def make_record(
    record_id: str,
    file_id: str = "SRC-00",
    statement: str = "Project scope rule for validation testing.",
    trace: list[str] | None = None,
    line_number: int = 1,
) -> Record:
    class_name = "SOURCE"
    authority_level = 2
    if file_id == "GOV-00":
        class_name = "GOVERNANCE"
        authority_level = 0
    elif file_id == "SRC-INDEX":
        class_name = "INDEX"
        authority_level = 1
    return Record(
        id=record_id,
        file=file_id,
        class_name=class_name,
        type="DECLARES",
        scope=[file_id],
        authority_level=authority_level,
        statement=statement,
        violation="Violation text.",
        action="ACTION",
        verification="Verification text.",
        trace=[] if trace is None else trace,
        source_path=Path(f"{file_id}.jsonl"),
        line_number=line_number,
    )

