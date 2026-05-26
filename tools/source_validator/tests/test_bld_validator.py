import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from source_validator.core.models import Record
from source_validator.core.record_index import build_record_index
from source_validator.validators.bld_guardrail_validator import validate_bld_guardrails
from source_validator.validators.bld_statement_grammar_validator import validate_bld_statement_grammar
from source_validator.validators.bld_template_validator import validate_bld_template
from source_validator.validators.bld_trace_validator import validate_bld_trace_resolution
from helpers import make_record


def make_bld_record(
    record_id: str,
    file_id: str = "BLD-01",
    statement: str = "kind=TEST;target=test;responsibility=validation",
    trace: list[str] | None = None,
    line_number: int = 1,
) -> Record:
    class_name = "INDEX" if file_id == "BLD-INDEX" else "BUILD"
    authority_level = 3 if file_id == "BLD-INDEX" else 4
    return Record(
        id=record_id,
        file=file_id,
        class_name=class_name,
        type="MUST",
        scope=[file_id],
        authority_level=authority_level,
        statement=statement,
        violation="Violation text.",
        action="ACTION",
        verification="Verification text.",
        trace=[] if trace is None else trace,
        source_path=Path(f"{file_id}__TEST__BUILD__SYSTEM.jsonl"),
        line_number=line_number,
    )


def full_template_records(file_id: str = "BLD-01") -> list[Record]:
    statements = {
        "FILE": "kind=FILE;target=BLD_file;responsibility=metadata",
        "ROLE": "kind=ROLE;target=BLD_file;responsibility=role",
        "SCOPE": "kind=SCOPE;target=BLD_file;responsibility=scope",
        "READ": "kind=READ;source=GOV-00;trace_to=exact_ids",
        "SRC": "kind=SRC;source=SRC-01;trace_to=exact_ids",
        "TARGET": "target=ledger_core;responsibility=own_transfer_boundary",
        "CONTRACT": "target=ledger_core;input=request;output=result",
        "PIPELINE": "pipeline_step=validate;order=1",
        "STRUCTURE": "kind=STRUCTURE;target=module;responsibility=boundary",
        "STATE": "state=journal;responsibility=owned_state",
        "DATA": "kind=DATA;target=entry;responsibility=data_boundary",
        "FAILURE": "failure=invalid_request;must=reject",
        "FORBID": "must_not=partial_commit",
        "TEST": "test=source_grounded_transfer_test",
        "REVIEW": "review=source_trace_review",
        "STOP": "stop_if=missing_authority",
    }
    return [
        make_bld_record(f"{file_id}-{family}-001", file_id, statement, ["GOV-BLD-006"], line_number=index)
        for index, (family, statement) in enumerate(statements.items(), start=1)
    ]


class BldValidatorTests(unittest.TestCase):
    def test_missing_required_bld_family_is_blocking(self):
        records = [record for record in full_template_records() if "-FORBID-" not in record.id]

        issues = validate_bld_template(records)

        self.assertTrue(any(issue.category == "BLD_TEMPLATE_MISSING_FAMILY" and issue.severity == "BLOCKING" for issue in issues))

    def test_missing_target_token_is_blocking(self):
        record = make_bld_record("BLD-01-TARGET-001", statement="responsibility=own_transfer_boundary")

        issues = validate_bld_statement_grammar([record])

        self.assertTrue(any(issue.category == "BLD_TARGET_MISSING_TARGET_TOKEN" and issue.severity == "BLOCKING" for issue in issues))

    def test_missing_contract_io_token_is_blocking(self):
        record = make_bld_record("BLD-01-CONTRACT-001", statement="target=ledger_core")

        issues = validate_bld_statement_grammar([record])

        self.assertTrue(any(issue.category == "BLD_CONTRACT_MISSING_IO_TOKEN" and issue.severity == "BLOCKING" for issue in issues))

    def test_missing_forbid_token_is_blocking(self):
        record = make_bld_record("BLD-01-FORBID-001", statement="target=ledger_core")

        issues = validate_bld_statement_grammar([record])

        self.assertTrue(any(issue.category == "BLD_FORBID_MISSING_PROHIBITION_TOKEN" and issue.severity == "BLOCKING" for issue in issues))

    def test_missing_stop_if_token_is_blocking(self):
        record = make_bld_record("BLD-01-STOP-001", statement="target=ledger_core")

        issues = validate_bld_statement_grammar([record])

        self.assertTrue(any(issue.category == "BLD_STOP_MISSING_STOP_IF_TOKEN" and issue.severity == "BLOCKING" for issue in issues))

    def test_broken_trace_reference_is_blocking(self):
        record = make_bld_record("BLD-01-FILE-001", trace=["GOV-DOES-NOT-EXIST"])
        index = build_record_index([record])

        issues = validate_bld_trace_resolution([record], index)

        self.assertTrue(any(issue.category == "TRACE_UNRESOLVED" and issue.severity == "BLOCKING" for issue in issues))

    def test_duplicate_record_id_across_source_and_bld_is_blocking(self):
        source = make_record("PROJECT-DUPLICATE-001", "SRC-00", trace=["GOV-META-000"])
        bld = make_bld_record("PROJECT-DUPLICATE-001", "BLD-01", trace=["GOV-BLD-006"])

        index = build_record_index([source, bld])

        self.assertTrue(any(issue.category == "DUPLICATE_RECORD_ID" and issue.severity == "BLOCKING" for issue in index.issues))

    def test_bld_index_implementation_detail_is_blocking(self):
        record = make_bld_record(
            "BLD-INDEX-ROUTE-999",
            "BLD-INDEX",
            statement="Transfer execution order uses debit before credit in the Ledger Core.",
            trace=["GOV-BLD-006"],
        )

        issues = validate_bld_guardrails([record])

        self.assertTrue(any(issue.category == "BLD_INDEX_IMPLEMENTATION_DETAIL" and issue.severity == "BLOCKING" for issue in issues))

    def test_bld_00_missing_omission_justification_is_blocking(self):
        records = [
            make_bld_record("BLD-00-FILE-001", "BLD-00", "kind=FILE;target=BLD-00;responsibility=metadata"),
            make_bld_record("BLD-00-ROLE-001", "BLD-00", "kind=ROLE;target=BLD-00;responsibility=identity"),
            make_bld_record("BLD-00-SCOPE-001", "BLD-00", "kind=SCOPE;target=BLD-00;responsibility=project_scope"),
            make_bld_record("BLD-00-STOP-001", "BLD-00", "stop_if=missing_authority"),
        ]

        issues = validate_bld_template(records)

        self.assertTrue(any(issue.category == "BLD_TEMPLATE_MISSING_FAMILY" and issue.severity == "BLOCKING" for issue in issues))


if __name__ == "__main__":
    unittest.main()

