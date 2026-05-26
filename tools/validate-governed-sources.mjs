import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const ROOT = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const DOC_DIR = path.join(ROOT, 'doc');

const GOVERNED_FILES = [
  'GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl',
  'SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl',
  'SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl',
  'SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl',
  'SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl',
  'SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl',
  'SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl',
  'SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl',
  'SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl',
  'SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl',
  'SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl',
  'SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl',
  'SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl',
];

const REQUIRED_FIELDS = [
  'id',
  'file',
  'class',
  'type',
  'scope',
  'authority_level',
  'statement',
  'violation',
  'action',
  'verification',
  'trace',
];

const DELETED_RECORD_IDS = new Set([
  'SRC-INDEX-GENERATION-ORDER-006',
  'SRC-INDEX-GENERATION-ORDER-007',
  'SRC-INDEX-GENERATION-ORDER-008',
  'SRC-INDEX-GENERATION-ORDER-009',
  'SRC-INDEX-GENERATION-ORDER-010',
  'SRC-INDEX-GENERATION-ORDER-011',
  'SRC-INDEX-GENERATION-ORDER-012',
  'SRC-INDEX-BLD-PRECONDITION-001',
  'SRC-INDEX-BLD-PRECONDITION-002',
  'SRC-INDEX-BLD-PRECONDITION-003',
  'SRC-INDEX-BLD-PRECONDITION-004',
  'SRC-INDEX-BLD-PRECONDITION-005',
]);

const DOWNSTREAM_SCOPE_TOKENS = new Set(['BLD-INDEX', 'BLD-*', 'CODE', 'TEST_OUTPUT', 'REPORT']);

function statusLine(name, errors, passText = 'PASS') {
  return `${name}: ${errors.length === 0 ? passText : `FAIL (${errors.length})`}`;
}

function recordLocation(record) {
  return `${path.relative(ROOT, record.path)}:${record.line}`;
}

function parseGovernedFiles() {
  const records = [];
  const parseErrors = [];

  for (const fileName of GOVERNED_FILES) {
    const filePath = path.join(DOC_DIR, fileName);
    if (!fs.existsSync(filePath)) {
      parseErrors.push(`${path.relative(ROOT, filePath)}: missing governed file`);
      continue;
    }

    const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
    lines.forEach((line, index) => {
      if (line.trim() === '') return;
      try {
        records.push({
          path: filePath,
          line: index + 1,
          data: JSON.parse(line),
        });
      } catch (error) {
        parseErrors.push(`${path.relative(ROOT, filePath)}:${index + 1}: ${error.message}`);
      }
    });
  }

  return { records, parseErrors };
}

function buildIdIndex(records) {
  const byId = new Map();
  const duplicateErrors = [];
  for (const record of records) {
    const id = record.data.id;
    if (byId.has(id)) {
      duplicateErrors.push(`${id}: ${recordLocation(byId.get(id))} and ${recordLocation(record)}`);
      continue;
    }
    byId.set(id, record);
  }
  return { byId, duplicateErrors };
}

function validateRequiredFields(records) {
  const errors = [];
  for (const record of records) {
    const keys = Object.keys(record.data);
    const sameOrder = keys.length === REQUIRED_FIELDS.length
      && keys.every((key, index) => key === REQUIRED_FIELDS[index]);
    if (!sameOrder) {
      errors.push(`${recordLocation(record)} ${record.data.id ?? '<missing id>'}: fields=${keys.join(',')}`);
      continue;
    }
    if (!Array.isArray(record.data.scope) || record.data.scope.length === 0) {
      errors.push(`${recordLocation(record)} ${record.data.id}: scope must be a non-empty array`);
    }
    if (!Array.isArray(record.data.trace)) {
      errors.push(`${recordLocation(record)} ${record.data.id}: trace must be an array`);
    }
  }
  return errors;
}

function validateTraceResolution(records, byId) {
  const errors = [];
  for (const record of records) {
    const trace = Array.isArray(record.data.trace) ? record.data.trace : [];
    for (const ref of trace) {
      if (!byId.has(ref)) {
        errors.push(`${recordLocation(record)} ${record.data.id}: unresolved trace ${ref}`);
      }
    }
  }
  return errors;
}

function representativeCycleFrom(start, componentSet, graph) {
  const stack = [{ node: start, nextIndex: 0 }];
  const seenIndex = new Map([[start, 0]]);

  while (stack.length > 0) {
    const top = stack[stack.length - 1];
    const neighbors = (graph.get(top.node) ?? []).filter((id) => componentSet.has(id));
    if (top.nextIndex >= neighbors.length) {
      seenIndex.delete(top.node);
      stack.pop();
      continue;
    }

    const next = neighbors[top.nextIndex];
    top.nextIndex += 1;
    if (seenIndex.has(next)) {
      const cycle = stack.slice(seenIndex.get(next)).map((entry) => entry.node);
      cycle.push(next);
      return cycle;
    }
    seenIndex.set(next, stack.length);
    stack.push({ node: next, nextIndex: 0 });
  }

  return [start, start];
}

function validateTraceCycles(records, byId) {
  const graph = new Map();
  for (const record of records) {
    const trace = Array.isArray(record.data.trace) ? record.data.trace : [];
    graph.set(record.data.id, trace.filter((ref) => byId.has(ref)));
  }

  const indexById = new Map();
  const lowById = new Map();
  const stack = [];
  const onStack = new Set();
  const cyclicComponents = [];

  function visit(id) {
    indexById.set(id, indexById.size);
    lowById.set(id, indexById.get(id));
    stack.push(id);
    onStack.add(id);

    for (const ref of graph.get(id) ?? []) {
      if (!indexById.has(ref)) {
        visit(ref);
        lowById.set(id, Math.min(lowById.get(id), lowById.get(ref)));
      } else if (onStack.has(ref)) {
        lowById.set(id, Math.min(lowById.get(id), indexById.get(ref)));
      }
    }

    if (lowById.get(id) === indexById.get(id)) {
      const component = [];
      let next;
      do {
        next = stack.pop();
        onStack.delete(next);
        component.push(next);
      } while (next !== id);

      const hasSelfLoop = component.length === 1 && (graph.get(component[0]) ?? []).includes(component[0]);
      if (component.length > 1 || hasSelfLoop) {
        cyclicComponents.push(component);
      }
    }
  }

  for (const id of graph.keys()) {
    if (!indexById.has(id)) visit(id);
  }

  return cyclicComponents.map((component) => {
    const componentSet = new Set(component);
    return representativeCycleFrom(component[0], componentSet, graph).join(' -> ');
  });
}

function parseAuthorizedScopes(records) {
  const govReg = records.find((record) => record.data.id === 'GOV-REG-003');
  if (!govReg) return { authorizedScopes: new Set(), errors: ['Missing GOV-REG-003'] };

  const match = String(govReg.data.statement).match(/AUTHORIZED_SCOPES=\[(.*)\]/);
  if (!match) return { authorizedScopes: new Set(), errors: [`${recordLocation(govReg)} GOV-REG-003: cannot parse AUTHORIZED_SCOPES`] };

  return {
    authorizedScopes: new Set(match[1].split(',').map((token) => token.trim()).filter(Boolean)),
    errors: [],
  };
}

function parseAggregateScopes(records) {
  const govScope = records.find((record) => record.data.id === 'GOV-SCOPE-004');
  if (!govScope) return { aggregateScopes: new Set(), errors: ['Missing GOV-SCOPE-004'] };

  const match = String(govScope.data.statement).match(/tokens are (.*)\./);
  if (!match) return { aggregateScopes: new Set(), errors: [`${recordLocation(govScope)} GOV-SCOPE-004: cannot parse aggregate scope tokens`] };

  const tokens = match[1]
    .replace(/\band\b/g, ',')
    .split(',')
    .map((token) => token.trim())
    .filter(Boolean);

  return { aggregateScopes: new Set(tokens), errors: [] };
}

function isExactFileScope(token) {
  return token === 'GOV-00'
    || token === 'SRC-INDEX'
    || token === 'BLD-INDEX'
    || /^SRC-\d{2}$/.test(token)
    || /^BLD-\d{2}$/.test(token);
}

function isWildcardScope(token) {
  return token === 'SRC-*' || token === 'BLD-*';
}

function validateScopes(records) {
  const { authorizedScopes, errors: registryErrors } = parseAuthorizedScopes(records);
  const { aggregateScopes, errors: aggregateErrors } = parseAggregateScopes(records);
  const errors = [...registryErrors, ...aggregateErrors];

  for (const token of aggregateScopes) {
    if (!authorizedScopes.has(token)) {
      errors.push(`GOV-SCOPE-004 declares ${token}, but GOV-REG-003 does not authorize it`);
    }
  }

  for (const record of records) {
    const scope = Array.isArray(record.data.scope) ? record.data.scope : [];
    for (const token of scope) {
      if (!authorizedScopes.has(token)) {
        errors.push(`${recordLocation(record)} ${record.data.id}: undeclared scope ${token}`);
        continue;
      }
      if (!isExactFileScope(token) && !isWildcardScope(token) && !aggregateScopes.has(token)) {
        errors.push(`${recordLocation(record)} ${record.data.id}: scope ${token} is authorized but not declared as exact, wildcard, or aggregate`);
      }
    }
  }

  if (!aggregateScopes.has('SYSTEM')) {
    errors.push('GOV-SCOPE-004 must declare SYSTEM as an aggregate scope token');
  }
  if (!authorizedScopes.has('SYSTEM')) {
    errors.push('GOV-REG-003 must authorize SYSTEM');
  }

  return errors;
}

function expectedAuthorityLevel(fileId) {
  if (fileId === 'GOV-00') return 0;
  if (fileId === 'SRC-INDEX') return 1;
  if (/^SRC-\d{2}$/.test(fileId)) return 2;
  return null;
}

function parseAuthorityLevels(records) {
  const govAuth = records.find((record) => record.data.id === 'GOV-AUTH-010');
  if (!govAuth) return { levels: new Map(), errors: ['Missing GOV-AUTH-010'] };

  const levels = new Map();
  for (const match of String(govAuth.data.statement).matchAll(/([A-Z0-9*-]+)=([0-9]+)/g)) {
    levels.set(match[1], Number(match[2]));
  }
  return { levels, errors: [] };
}

function validateAuthorityLevels(records) {
  const errors = [];
  for (const record of records) {
    const expected = expectedAuthorityLevel(record.data.file);
    if (expected !== null && record.data.authority_level !== expected) {
      errors.push(`${recordLocation(record)} ${record.data.id}: authority_level ${record.data.authority_level}, expected ${expected}`);
    }
  }

  const { levels, errors: parseErrors } = parseAuthorityLevels(records);
  errors.push(...parseErrors);
  if (levels.has('TRACE') && levels.has('REPORT') && !(levels.get('TRACE') < levels.get('REPORT'))) {
    errors.push(`GOV-AUTH-010 must assign TRACE higher precedence than REPORT; got TRACE=${levels.get('TRACE')} REPORT=${levels.get('REPORT')}`);
  }

  return errors;
}

function validateDeletedRecordSafety(records) {
  const errors = [];
  for (const record of records) {
    if (DELETED_RECORD_IDS.has(record.data.id)) {
      errors.push(`${recordLocation(record)} ${record.data.id}: deleted overreach record is still active`);
    }

    const trace = Array.isArray(record.data.trace) ? record.data.trace : [];
    for (const ref of trace) {
      if (DELETED_RECORD_IDS.has(ref)) {
        errors.push(`${recordLocation(record)} ${record.data.id}: traces to deleted record ${ref}`);
      }
    }
  }
  return errors;
}

function validateSrcIndexBoundary(records) {
  const errors = [];
  const srcIndexRecords = records.filter((record) => record.data.file === 'SRC-INDEX');

  for (const record of srcIndexRecords) {
    const id = String(record.data.id);
    const scope = Array.isArray(record.data.scope) ? record.data.scope : [];
    if (/^SRC-INDEX-BLD-PRECONDITION-/.test(id)) {
      errors.push(`${recordLocation(record)} ${id}: BLD implementation precondition is outside SRC-INDEX authority`);
    }
    if (/^SRC-INDEX-GENERATION-ORDER-/.test(id) && scope.some((token) => DOWNSTREAM_SCOPE_TOKENS.has(token))) {
      errors.push(`${recordLocation(record)} ${id}: downstream generation scope ${scope.join(',')}`);
    }
  }

  return errors;
}

const { records, parseErrors } = parseGovernedFiles();
const { byId, duplicateErrors } = buildIdIndex(records);
const requiredFieldErrors = validateRequiredFields(records);
const traceResolutionErrors = validateTraceResolution(records, byId);
const traceCycleErrors = validateTraceCycles(records, byId);
const scopeErrors = validateScopes(records);
const authorityErrors = validateAuthorityLevels(records);
const deletedRecordErrors = validateDeletedRecordSafety(records);
const boundaryErrors = validateSrcIndexBoundary(records);

const sections = [
  ['JSONL parse', parseErrors],
  ['Required fields', requiredFieldErrors],
  ['Duplicate IDs', duplicateErrors],
  ['Trace resolution', traceResolutionErrors],
  ['Trace cycles', traceCycleErrors, 'PASS / zero cycles'],
  ['Scope registry', scopeErrors],
  ['Authority levels', authorityErrors],
  ['Deleted-record trace safety', deletedRecordErrors],
  ['SRC-INDEX boundary', boundaryErrors],
];

console.log(`governed_files: ${GOVERNED_FILES.length}`);
console.log(`records: ${records.length}`);
for (const [name, errors, passText] of sections) {
  console.log(statusLine(name, errors, passText));
}

const allErrors = sections.flatMap(([, errors]) => errors);
if (allErrors.length > 0) {
  console.log('\nValidation errors:');
  for (const error of allErrors) {
    console.log(`- ${error}`);
  }
  console.log('\nVALIDATION_STATUS: FAIL');
  process.exit(1);
}

console.log('\nVALIDATION_STATUS: PASS');
