Validator for the project's governed JSONL sources.

Usage:

Run from the repository root (Windows):

```powershell
python tools\validator.py
```

Output:
- Prints a JSON report to stdout
- Writes `tools/validator_baseline.json` with detailed results

Notes:
- The validator enforces strict JSONL parsing, canonical field order, duplicate id detection, basic file-field matching, authority level rules (GOV files -> 0, SRC* -> 1), trace resolution after full-file collection, detection of self-traces, and basic TEST mapping presence checks.
