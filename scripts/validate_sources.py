from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REQUIRED_FIELDS = [
    'id', 'file', 'class', 'type', 'scope', 'authority_level',
    'statement', 'violation', 'action', 'verification', 'trace',
]

AUTHORIZED_TYPES = {
    'DECLARES', 'MUST', 'MUST_NOT', 'SHOULD', 'MAY', 'OVERRIDES', 'REQUIRES', 'FORBIDS',
}

AUTHORIZED_CLASSES = {
    'GOVERNANCE', 'INDEX', 'SOURCE', 'BUILD', 'CODE', 'TEST_OUTPUT', 'TRACE', 'REPORT',
}

KNOWN_DUPLICATE_GROUPS = [
    ['UPG-015', 'FAIL-RULE-008', 'FAIL-RULE-501'],
    ['AUTH-READMODEL-005', 'READ-010'],
    ['AUTH-READMODEL-007', 'READ-014'],
    ['BOOT-004', 'ASSET-012'],
    ['FAIL-RULE-301', 'FAIL-RULE-007', 'IDEMP-051'],
    ['FORBID-015', 'FORBID-088'],
    ['FORBID-016', 'FORBID-089'],
    ['FORBID-017', 'FORBID-090'],
    ['FORBID-018', 'FORBID-091'],
    ['FORBID-026', 'FORBID-082'],
]


def load_records(root: Path):
    paths = [root] if root.is_file() else sorted(root.glob('*.jsonl'))
    records = []
    errors = []
    for path in paths:
        for line_no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except Exception as exc:
                errors.append((str(path), line_no, 'JSON_PARSE', str(exc)))
                continue
            records.append((path, line_no, rec))
    return records, errors


def parse_authorized_scopes(records):
    for _path, _line_no, rec in records:
        if rec.get('id') == 'GOV-REG-003':
            stmt = rec.get('statement', '')
            match = re.search(r'AUTHORIZED_SCOPES=\[(.*)\]', stmt)
            if not match:
                raise RuntimeError('Could not parse GOV-REG-003 AUTHORIZED_SCOPES')
            return {part.strip() for part in match.group(1).split(',') if part.strip()}
    raise RuntimeError('Missing GOV-REG-003')


def expected_authority_level(file_id: str | None):
    if file_id == 'GOV-00':
        return 0
    if file_id == 'SRC-INDEX':
        return 1
    if re.fullmatch(r'SRC-\d{2}', file_id or ''):
        return 2
    if file_id == 'BLD-INDEX':
        return 3
    if re.fullmatch(r'BLD-\d{2}', file_id or ''):
        return 4
    return None


def expected_file_id(path: Path):
    name = path.name
    if '__' not in name:
        return None
    return name.split('__', 1)[0]


def parse_namespace_owners(records):
    owners = {}
    for _path, _line_no, rec in records:
        if not str(rec.get('id', '')).startswith('SRC-INDEX-NAMESPACE-'):
            continue
        match = re.match(r'([A-Z0-9-]+)\* ids are owned by (SRC-\d{2})\.', rec.get('statement', ''))
        if match:
            owners[match.group(1)] = match.group(2)
    return owners


def expected_owner_for_id(record_id: str, namespace_owners: dict[str, str]):
    matches = [(prefix, owner) for prefix, owner in namespace_owners.items() if record_id.startswith(prefix)]
    if not matches:
        return None
    return max(matches, key=lambda item: len(item[0]))[1]


def contains_all(statement: str, parts: list[str]):
    return all(part in statement for part in parts)


def semantic_checks(by_id: dict):
    errors = []

    for group in KNOWN_DUPLICATE_GROUPS:
        present = [(rid, by_id[rid][2].get('statement', '')) for rid in group if rid in by_id]
        seen = {}
        for rid, statement in present:
            if statement in seen:
                errors.append(('DUPLICATE_GROUP_STATEMENT', rid, seen[statement], statement))
            seen[statement] = rid

    result_037 = by_id.get('RESULT-037', (None, None, {}))[2].get('statement', '')
    expected_fields = [
        'operationId', 'requestId', 'idempotencyKey', 'operationType', 'status',
        'sourceAccountId', 'destinationAccountId', 'assetId', 'amountMinorUnits',
        'ledgerEntryIds', 'canonicalTimestamp',
    ]
    if not contains_all(result_037, expected_fields) or 'optional' in result_037.lower() or 'amount,' in result_037:
        errors.append(('RESULT_FIELD_ORDER', 'RESULT-037', result_037))

    result_039 = by_id.get('RESULT-039', (None, None, {}))[2].get('statement', '')
    if not contains_all(result_039, ['exactly 9 fractional digits', 'trailing Z', 'no timezone offset other than Z']):
        errors.append(('RESULT_TIMESTAMP_ENCODING', 'RESULT-039', result_039))

    result_043 = by_id.get('RESULT-043', (None, None, {}))[2].get('statement', '')
    if not contains_all(result_043, ['debit LedgerEntry first', 'credit LedgerEntry second']):
        errors.append(('RESULT_LEDGER_ENTRY_ORDER', 'RESULT-043', result_043))

    result_023 = by_id.get('RESULT-023', (None, None, {}))[2].get('statement', '')
    if not contains_all(result_023, ['SHA-256', 'canonical serialized committed result bytes', 'lowercase hexadecimal']):
        errors.append(('RESULT_HASH_ENCODING', 'RESULT-023', result_023))

    result_044 = by_id.get('RESULT-044', (None, None, {}))[2].get('statement', '')
    if not contains_all(result_044, ['FAIL-* record id', 'uppercase ASCII']):
        errors.append(('RESULT_ERROR_CODE_ENCODING', 'RESULT-044', result_044))

    idem_089 = by_id.get('IDEMP-089', (None, None, {}))[2].get('statement', '')
    fingerprint_terms = [
        'operationType', 'sourceAccountId', 'destinationAccountId', 'assetId',
        'amountMinorUnits', 'SHA-256', 'lowercase hexadecimal', 'no-whitespace JSON',
    ]
    if not contains_all(idem_089, fingerprint_terms):
        errors.append(('IDEMP_REQUEST_FINGERPRINT', 'IDEMP-089', idem_089))

    amount_032 = by_id.get('AMOUNT-032', (None, None, {}))[2].get('statement', '')
    amount_035 = by_id.get('AMOUNT-035', (None, None, {}))[2].get('statement', '')
    if 'canonicalization strips redundant leading zeros' in amount_032 or '0001.00' in amount_032:
        errors.append(('AMOUNT_LEADING_ZERO_CONFLICT', 'AMOUNT-032', amount_032))
    if 'must not canonicalize redundant leading zeros' not in amount_035:
        errors.append(('AMOUNT_LEADING_ZERO_POLICY', 'AMOUNT-035', amount_035))

    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('doc')
    records, json_errors = load_records(root)

    by_id = {}
    field_errors = []
    ids = []
    for path, line_no, rec in records:
        rid = rec.get('id')
        ids.append(rid)
        if list(rec.keys()) != REQUIRED_FIELDS:
            field_errors.append((path, line_no, rid, list(rec.keys())))
        if rid in by_id:
            pass
        by_id[rid] = (path, line_no, rec)

    id_counts = Counter(ids)
    duplicates = [rid for rid, count in id_counts.items() if count > 1]

    try:
        authorized_scopes = parse_authorized_scopes(records)
        scope_parse_errors = []
    except Exception as exc:
        authorized_scopes = set()
        scope_parse_errors = [(str(root), 0, 'AUTHORIZED_SCOPE_PARSE', str(exc))]

    invalid_types = []
    invalid_classes = []
    invalid_scopes = []
    invalid_trace_shapes = []
    unresolved_traces = []
    authority_level_errors = []
    file_field_errors = []
    owner_errors = []
    namespace_owners = parse_namespace_owners(records)

    for path, line_no, rec in records:
        rid = rec.get('id')

        if rec.get('type') not in AUTHORIZED_TYPES:
            invalid_types.append((path, line_no, rid, rec.get('type')))

        if rec.get('class') not in AUTHORIZED_CLASSES:
            invalid_classes.append((path, line_no, rid, rec.get('class')))

        scope = rec.get('scope')
        if not isinstance(scope, list) or not scope:
            invalid_scopes.append((path, line_no, rid, scope, 'SCOPE_NOT_NONEMPTY_ARRAY'))
        else:
            for token in scope:
                if token not in authorized_scopes:
                    invalid_scopes.append((path, line_no, rid, token, 'UNDECLARED_SCOPE'))

        trace = rec.get('trace')
        if not isinstance(trace, list):
            invalid_trace_shapes.append((path, line_no, rid, trace))
        else:
            for ref in trace:
                if ref not in by_id:
                    unresolved_traces.append((path, line_no, rid, ref))

        expected = expected_authority_level(rec.get('file'))
        if expected is not None and rec.get('authority_level') != expected:
            authority_level_errors.append((path, line_no, rid, rec.get('file'), rec.get('authority_level'), expected))

        expected_file = expected_file_id(path)
        if expected_file is not None and rec.get('file') != expected_file:
            file_field_errors.append((path, line_no, rid, rec.get('file'), expected_file))

        owner = expected_owner_for_id(str(rid), namespace_owners)
        if owner is not None and rec.get('file') != owner:
            owner_errors.append((path, line_no, rid, rec.get('file'), owner))

    semantic_errors = semantic_checks(by_id)

    print(f'files_root: {root}')
    print(f'records: {len(records)}')
    print(f'json_errors: {len(json_errors) + len(scope_parse_errors)}')
    print(f'duplicate_ids: {len(duplicates)}')
    print(f'field_order_errors: {len(field_errors)}')
    print(f'invalid_types: {len(invalid_types)}')
    print(f'invalid_classes: {len(invalid_classes)}')
    print(f'invalid_scope_tokens: {len(invalid_scopes)}')
    print(f'invalid_trace_shapes: {len(invalid_trace_shapes)}')
    print(f'unresolved_trace_refs: {len(unresolved_traces)}')
    print(f'authority_level_errors: {len(authority_level_errors)}')
    print(f'file_field_errors: {len(file_field_errors)}')
    print(f'id_owner_errors: {len(owner_errors)}')
    print(f'semantic_errors: {len(semantic_errors)}')

    if unresolved_traces:
        print('\nTop unresolved trace IDs:')
        for ref, count in Counter(ref for *_rest, ref in unresolved_traces).most_common(50):
            print(f'  {ref}: {count}')

    failures = (
        json_errors or scope_parse_errors or duplicates or field_errors or invalid_types or invalid_classes or
        invalid_scopes or invalid_trace_shapes or unresolved_traces or authority_level_errors or
        file_field_errors or owner_errors or semantic_errors
    )
    if failures:
        print('\nVALIDATION_STATUS: FAIL')
        return 1

    print('\nVALIDATION_STATUS: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
