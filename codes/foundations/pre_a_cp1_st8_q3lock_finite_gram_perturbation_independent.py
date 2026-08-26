#!/usr/bin/env python3
"""Independent exact finite Gram-entry perturbation audit for EXP-001178."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-gram-perturbation"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R339.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
MARKER = "finite_gram_entry_perturbation"


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


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    f = tuple(tuple(Fraction(int(value)) for value in row) for row in fixture["f"])
    g = tuple(tuple(Fraction(int(value)) for value in row) for row in fixture["g"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", (manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")) == ("EXP-001178", "T-054", False), [manifest.get("exploration_id"), manifest.get("task_id"), manifest.get("claim_bearing")], ["EXP-001178", "T-054", False], "provenance")
    check("fixture shape", len(f) == 2 and len(g) == 2 and {len(row) for row in f + g} == {3}, [len(f), len(g), sorted({len(row) for row in f + g})], "2 rows x 3 coordinates", "fixture")
    source_lines = LEAN.read_text(encoding="utf-8").splitlines()
    declarations = [line.strip().split()[1] for line in source_lines if line.strip().startswith(("theorem ", "lemma ", "example "))]
    check("declaration set", tuple(declarations) == (MARKER,), declarations, [MARKER], "Lean")
    forbidden = {token: sum(1 for line in source_lines if re.search(rf"\b{re.escape(token)}\b", line)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("forbidden token scan", all(value == 0 for value in forbidden.values()), forbidden, {token: 0 for token in forbidden}, "Lean")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    matches = [item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R339.lean"]
    check("registry uniqueness", len(matches) == 1, len(matches), 1, "registry")
    check("registry hash", matches[0]["sha256"] == source_hash(LEAN), matches[0]["sha256"], source_hash(LEAN), "registry")
    rows: list[dict[str, Any]] = []
    for i, (fi, gi) in enumerate(zip(f, g)):
        for j, (fj, gj) in enumerate(zip(f, g)):
            gram_f = sum(value * fi[k] for k, value in enumerate(fj))
            gram_g = sum(value * gi[k] for k, value in enumerate(gj))
            lhs = abs(gram_f - gram_g)
            left = sum(abs(fi[k] - gi[k]) * abs(fj[k]) for k in range(len(fi)))
            right = sum(abs(gi[k]) * abs(fj[k] - gj[k]) for k in range(len(fi)))
            rhs = left + right
            check(f"pair ({i},{j}) exact inequality", lhs <= rhs, [lhs, rhs], "lhs <= rhs", "fixture")
            check(f"pair ({i},{j}) exact slack", rhs - lhs >= 0, rhs - lhs, ">=0", "fixture")
            rows.append({"i": i, "j": j, "G_f": str(gram_f), "G_g": str(gram_g), "lhs": str(lhs), "left_word_term": str(left), "right_word_term": str(right), "rhs": str(rhs), "slack": str(rhs - lhs)})
    check("scope", manifest["scope"]["finite_gram_perturbation_closed"] and manifest["scope"]["finite_fixture_reproduced"] and not manifest["scope"]["actual_q3_os_vector_factorization_closed"], manifest["scope"], "finite bridge only", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GRAM-PERTURBATION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "formal_checks": [MARKER],
        "rows": rows,
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
        "provenance": {"script_sha256": source_hash(Path(__file__)), "manifest_sha256": source_hash(MANIFEST), "lean_sha256": source_hash(LEAN)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-GRAM-PERTURBATION PASS {payload['passed']}/{payload['assertion_count']} pairs={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
