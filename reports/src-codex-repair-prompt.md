# Codex SRC Repair Prompt

You are repairing governed GOV/SRC JSONL source authority files after deterministic SRC-only validation.

Do not change BLD files. Do not create BLD validators. Do not infer new GOV/SRC rules.
Stop after the listed BLOCKING and ERROR issues are resolved and rerun the SRC validator.

Verdict: WARNING_ONLY
Blocking/Error issue count: 0

## Failed Records

No BLOCKING or ERROR issues were detected. Review WARNING items only if desired.

## Files Likely Needing Edits

- None

## Stop Conditions

- Stop if a suggested fix would require creating or validating BLD files.
- Stop if fixing an issue requires changing project semantics rather than correcting structure, trace, namespace, or ownership mechanics.
- Stop after deterministic validation reaches PASS or WARNING_ONLY for the targeted fix set.

## Do-Not-Change Warnings

- Do not modify implementation app code.
- Do not use README, runtime behavior, tests, generated output, or chat history as source authority.
- Do not broaden SRC-10 from proof/risk/DoD authority into domain/source authority.