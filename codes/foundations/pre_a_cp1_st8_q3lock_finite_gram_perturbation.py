#!/usr/bin/env python3
"""Primary exact finite Gram-entry perturbation audit for EXP-001178."""

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
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
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


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def to_fraction(value: Any) -> Fraction:
    return Fraction(int(value))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    f = [[to_fraction(value) for value in row] for row in fixture["f"]]
    g = [[to_fraction(value) for value in row] for row in fixture["g"]]
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001178" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001178/T-054", "provenance")
    check("fixture shape", len(f) == fixture["index_count"] and len(g) == fixture["index_count"] and all(len(row) == fixture["coordinate_count"] for row in f + g), [len(f), len(g), [len(row) for row in f + g]], "2 rows x 3 coordinates", "fixture")
    check("claim firewall", manifest["claim_bearing"] is False and not manifest["scope"]["actual_q3_os_vector_factorization_closed"], [manifest["claim_bearing"], manifest["scope"]["actual_q3_os_vector_factorization_closed"]], "nonbearing/open", "scope")
    source = LEAN.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item["path"] == "verification/lean/Tect/R339.lean"), None)
    declarations = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("Lean marker", MARKER in declarations, declarations, MARKER, "Lean")
    check("registry hash", entry is not None and entry["sha256"] == normalized_sha256(LEAN), entry["sha256"] if entry else None, normalized_sha256(LEAN), "Lean")
    rows: list[dict[str, Any]] = []
    for i in range(len(f)):
        for j in range(len(f)):
            gram_f = sum(f[i][k] * f[j][k] for k in range(len(f[i])))
            gram_g = sum(g[i][k] * g[j][k] for k in range(len(g[i])))
            lhs = abs(gram_f - gram_g)
            left = sum(abs(f[i][k] - g[i][k]) * abs(f[j][k]) for k in range(len(f[i])))
            right = sum(abs(g[i][k]) * abs(f[j][k] - g[j][k]) for k in range(len(f[i])))
            rhs = left + right
            slack = rhs - lhs
            check(f"pair ({i},{j}) inequality", lhs <= rhs, [lhs, rhs], "lhs <= rhs", "fixture")
            check(f"pair ({i},{j}) nonnegative slack", slack >= 0, slack, ">=0", "fixture")
            rows.append({"i": i, "j": j, "G_f": str(gram_f), "G_g": str(gram_g), "lhs": str(lhs), "left_word_term": str(left), "right_word_term": str(right), "rhs": str(rhs), "slack": str(slack)})
    check("pair coverage", len(rows) == len(f) * len(f), len(rows), len(f) * len(f), "coverage")
    check("finite fixture closed", manifest["scope"]["finite_gram_perturbation_closed"] and manifest["scope"]["finite_fixture_reproduced"], manifest["scope"], "finite theorem and fixture", "scope")
    check("QFT firewall", all(not manifest["scope"][field] for field in ("actual_q3_os_vector_factorization_closed", "common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "pre_a_closed")), manifest["scope"], "downstream gates open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GRAM-PERTURBATION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "formal_checks": [MARKER],
        "rows": rows,
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
        "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-GRAM-PERTURBATION PASS {payload['passed']}/{payload['assertion_count']} pairs={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
