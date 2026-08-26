#!/usr/bin/env python3
"""Independent structural audit for the R338 finite QFT algebra cross-check."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-lean-finite-algebra"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R338.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
MARKERS = (
    "finite_trace_cyclicity",
    "finite_thermal_four_cycle",
    "finite_os_gram_real_possemidef",
    "finite_transfer_scope",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def lf_hash(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    source_lines = LEAN.read_text(encoding="utf-8").splitlines()
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")) == ("EXP-001177", "T-054", False), [manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")], ["EXP-001177", "T-054", False], "provenance")
    check("source exists", bool(source_lines) and source_lines[-1] == "end Tect.R338", bool(source_lines), "LF-terminated Lean source", "source")
    theorem_lines = [line.strip().split()[1] for line in source_lines if line.strip().startswith(("theorem ", "lemma ", "example "))]
    check("declaration order", tuple(theorem_lines) == MARKERS, theorem_lines, list(MARKERS), "source")
    token_hits = {token: sum(1 for line in source_lines if re.search(rf"\b{re.escape(token)}\b", line)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("forbidden token scan", all(count == 0 for count in token_hits.values()), token_hits, {token: 0 for token in ("sorry", "admit", "axiom", "unsafe")}, "source")
    registry_paths = [item.get("path") for item in registry.get("entrypoints", [])]
    check("registry coverage", registry_paths.count("verification/lean/Tect/R338.lean") == 1, registry_paths.count("verification/lean/Tect/R338.lean"), 1, "registry")
    entry = next(item for item in registry["entrypoints"] if item["path"] == "verification/lean/Tect/R338.lean")
    check("registry hash", entry.get("sha256") == lf_hash(LEAN), entry.get("sha256"), lf_hash(LEAN), "registry")
    check("registry marker set", tuple(entry.get("declarations", [])) == MARKERS, entry.get("declarations"), list(MARKERS), "registry")
    closed = manifest["scope"]
    check("finite-only scope", all(closed[field] for field in ("finite_trace_cyclicity_closed", "finite_thermal_cyclicity_closed", "finite_os_gram_real_closed", "lean_entrypoint_registered")) and all(not closed[field] for field in ("common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), closed, "finite identities only; downstream QFT gates open", "scope")
    formal = tuple(MARKERS)
    check("formal marker set", set(formal) == set(theorem_lines), formal, list(MARKERS), "formal")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LEAN-FINITE-ALGEBRA",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "formal_checks": list(formal),
        "source_sha256": lf_hash(LEAN),
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LEAN-FINITE-ALGEBRA PASS {payload['passed']}/{payload['assertion_count']} markers={len(payload['formal_checks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
