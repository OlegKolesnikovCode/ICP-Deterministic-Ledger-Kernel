RESPONSIBILITY_MAP = {
    "SRC-00": [
        "project identity",
        "project thesis",
        "project scope",
        "project non-goal",
        "default decision",
        "adr ownership",
    ],
    "SRC-01": [
        "canister authority",
        "trusted gateway",
        "cross-canister",
        "caller",
        "permission authority",
    ],
    "SRC-02": [
        "domain entity",
        "entity identity",
        "account semantic",
        "asset semantic",
        "balance semantic",
        "amount representation",
    ],
    "SRC-03": [
        "transfer operation",
        "operation lifecycle",
        "transfer lifecycle",
        "operation result",
    ],
    "SRC-04": [
        "idempotency",
        "replay determinism",
        "duplicate behavior",
        "in_progress recovery",
    ],
    "SRC-05": [
        "ledger journal",
        "ledger entry",
        "balance invariant",
        "temporal anchoring",
        "commit atomicity",
    ],
    "SRC-06": [
        "failure model",
        "deterministic rejection",
    ],
    "SRC-07": [
        "read model",
        "sync rule",
        "freshness",
        "rebuild rule",
    ],
    "SRC-08": [
        "upgrade safety",
        "stable-state",
        "migration check",
        "maintenance mode",
    ],
    "SRC-09": [
        "api surface",
        "query semantics",
        "update semantics",
        "forbidden api",
    ],
    "SRC-10": [
        "test proof",
        "acceptance criteria",
        "falsifier",
        "risk",
        "definition of done",
    ],
}

OWNERSHIP_ASSERTION_TERMS = [
    " owns ",
    " is authoritative for ",
    " is the authority for ",
    " primary authority for ",
    " source truth for ",
]

IMPLEMENTATION_GUIDANCE_TERMS = [
    "implementation folder",
    "implementation path",
    "write code",
    "code file",
    "framework workflow",
    "dependency selection",
]
