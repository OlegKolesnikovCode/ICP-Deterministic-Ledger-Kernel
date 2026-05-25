#!/usr/bin/env python3
import os
import json
import sys
from collections import OrderedDict, defaultdict

CANONICAL_KEYS = [
    "id","file","class","type","scope","authority_level",
    "statement","violation","action","verification","trace"
]

DOC_DIR = os.path.join(os.getcwd(), "doc")
GOV_FILE = None
for name in os.listdir(DOC_DIR):
    if name.startswith("GOV-00") and name.endswith('.jsonl'):
        GOV_FILE = os.path.join(DOC_DIR, name)
        break


def load_jsonl(path):
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            raw = line.rstrip('\n')
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw, object_pairs_hook=OrderedDict)
                records.append((n, raw, obj))
            except Exception as e:
                records.append((n, raw, e))
    return records


def gather_all_records():
    files = []
    for fname in os.listdir(DOC_DIR):
        if fname.lower().endswith('.jsonl'):
            files.append(fname)
    all_recs = []
    parse_errors = []
    for fname in sorted(files):
        path = os.path.join(DOC_DIR, fname)
        loaded = load_jsonl(path)
        for n, raw, obj in loaded:
            if isinstance(obj, Exception):
                parse_errors.append({"file": fname, "line": n, "error": str(obj), "raw": raw})
            else:
                all_recs.append((fname, n, obj))
    return all_recs, parse_errors


def canonicalize_file_key(fname):
    return fname.split('__',1)[0]


def main():
    all_recs, parse_errors = gather_all_records()
    ids = defaultdict(list)
    duplicates = []
    field_order_errors = []
    file_mismatch = []
    authority_level_errors = []
    invalid_scope_records = []
    records_by_id = {}
    tests_defined = set()
    test_accept_traces = defaultdict(list)
    test_map_traces = defaultdict(list)

    # collect GOV authorized scope tokens if possible
    authorized_scopes = set()
    if GOV_FILE and os.path.exists(GOV_FILE):
        for _, _, obj in load_jsonl(GOV_FILE):
            if isinstance(obj, dict) and 'scope' in obj:
                for tok in obj['scope']:
                    authorized_scopes.add(tok)
            if isinstance(obj, dict) and 'statement' in obj:
                st = obj['statement']
                for token in ['SYSTEM','SRC-','BLD-','GOV-','TEST-','AUTH-','AUTH-CALLER-']:
                    if token in st:
                        authorized_scopes.add(token)

    # First pass: collect ids and basic checks
    for fname, line_no, obj in all_recs:
        if not isinstance(obj, dict):
            continue
        rid = obj.get('id')
        if not rid:
            continue
        ids[rid].append((fname, line_no))
        records_by_id[rid] = (fname, line_no, obj)
        # field order check
        if list(obj.keys()) != CANONICAL_KEYS:
            field_order_errors.append({"id": rid, "file": fname, "line": line_no, "keys": list(obj.keys())})
        # file-field match
        file_key = canonicalize_file_key(fname)
        if obj.get('file') != file_key:
            file_mismatch.append({"id": rid, "file": fname, "line": line_no, "record_file": obj.get('file'), "expected": file_key})
        # authority_level basic check
        al = obj.get('authority_level')
        try:
            if fname.startswith('GOV-'):
                if al != 0:
                    authority_level_errors.append({"id": rid, "file": fname, "line": line_no, "authority_level": al, "expected": 0})
            else:
                if al != 1:
                    authority_level_errors.append({"id": rid, "file": fname, "line": line_no, "authority_level": al, "expected": 1})
        except Exception:
            authority_level_errors.append({"id": rid, "file": fname, "line": line_no, "authority_level": al, "expected": "int"})
        # collect tests
        if rid.startswith('TEST-'):
            tests_defined.add(rid)
        # collect test-accept traces if present
        if rid.startswith('TEST-ACCEPT-') or rid.startswith('TEST-ACCEPT'):
            for t in obj.get('trace', []) if isinstance(obj.get('trace', []), list) else []:
                test_accept_traces[t].append(rid)
        if rid.startswith('TEST-MAP-'):
            for t in obj.get('trace', []) if isinstance(obj.get('trace', []), list) else []:
                test_map_traces[t].append(rid)

    duplicate_ids = [k for k, v in ids.items() if len(v) > 1]

    # Second pass: trace resolution and scope validation
    unresolved_traces = []
    self_traces = []
    for rid, (fname, line_no, obj) in records_by_id.items():
        traces = obj.get('trace', [])
        if not isinstance(traces, list):
            unresolved_traces.append({"id": rid, "file": fname, "line": line_no, "error": "trace-not-list"})
            continue
        for t in traces:
            if t == rid:
                self_traces.append({"id": rid, "file": fname, "line": line_no})
            if t not in records_by_id:
                unresolved_traces.append({"id": rid, "file": fname, "line": line_no, "missing_trace": t})
        # scope validation
        scope = obj.get('scope', [])
        if not isinstance(scope, list):
            invalid_scope_records.append({"id": rid, "file": fname, "line": line_no, "scope": scope})
        else:
            for tok in scope:
                if authorized_scopes and tok not in authorized_scopes:
                    invalid_scope_records.append({"id": rid, "file": fname, "line": line_no, "bad_scope": tok})

    # Tests mapping checks
    unmapped_tests = []
    tests_without_acceptance_criteria = []
    for t in sorted(tests_defined):
        mapped = False
        if t in test_map_traces and test_map_traces[t]:
            mapped = True
        for r in records_by_id.values():
            if t in (r[2].get('trace') or []):
                mapped = True
                break
        if not mapped:
            unmapped_tests.append(t)
        if t not in test_accept_traces:
            tests_without_acceptance_criteria.append(t)

    summary = {
        "json_parse_errors": len(parse_errors),
        "duplicate_ids": len(duplicate_ids),
        "field_order_errors": len(field_order_errors),
        "file_field_mismatches": len(file_mismatch),
        "authority_level_errors": len(authority_level_errors),
        "invalid_scope_records": len(invalid_scope_records),
        "unresolved_traces": len(unresolved_traces),
        "self_traces": len(self_traces),
        "unmapped_tests": len(unmapped_tests),
        "tests_without_acceptance_criteria": len(tests_without_acceptance_criteria),
    }

    out = {
        "summary": summary,
        "details": {
            "parse_errors": parse_errors[:20],
            "duplicate_ids": duplicate_ids[:50],
            "field_order_errors": field_order_errors[:20],
            "file_field_mismatches": file_mismatch[:20],
            "authority_level_errors": authority_level_errors[:20],
            "invalid_scope_records": invalid_scope_records[:20],
            "unresolved_traces": unresolved_traces[:50],
            "self_traces": self_traces[:20],
            "unmapped_tests_sample": unmapped_tests[:50],
            "tests_without_acceptance_criteria_sample": tests_without_acceptance_criteria[:50]
        }
    }

    print(json.dumps(out, indent=2))
    # also write baseline file
    with open(os.path.join('tools', 'validator_baseline.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)


if __name__ == '__main__':
    main()
