"""gates.py -- single source of truth for the generated-surface sync gates.

Both doctor.py (workspace readiness) and release_check.py (publication gate)
import SYNC_GATES, so the gate list can never drift between them. The
2026-06-09 doctor/release_check divergence (release_check gained index /
changelog / dossier gates that doctor.py never received) is the exact failure
mode this module prevents.

regen_all.py imports REGEN_ORDER to refresh every generated surface in
dependency order (build_catalog LAST, as it indexes everything else).

Each entry is (label, [script, *args]) with a BARE script name; each caller
prefixes the path it needs (doctor: SCRIPTS/<name>; release_check:
verification/scripts/<name>).
"""
__version__ = "1.0.0"

# --check sync gates (generated surface == its source). Order is display-only.
SYNC_GATES = [
    ("ledger",    ["lint_claims.py", "--render", "--check"]),
    ("catalog",   ["build_catalog.py", "--check"]),
    ("lineage",   ["build_lineage.py", "--check"]),
    ("index",     ["build_index.py", "--check"]),
    ("todo",      ["todo.py", "--check"]),
    ("changelog", ["changelog.py", "render", "--check"]),
    ("changelog-integrity", ["changelog.py", "verify"]),
    ("dossier",   ["build_dossier.py", "--check"]),
]

# Write (non-check) invocations, in dependency order. build_catalog is LAST
# because it indexes every other generated file.
REGEN_ORDER = [
    ["lint_claims.py", "--render"],
    ["build_lineage.py"],
    ["build_index.py"],
    ["build_dossier.py"],
    ["changelog.py", "render"],
    ["todo.py", "render"],
    ["build_catalog.py"],
]
