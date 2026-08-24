#!/usr/bin/env python3
"""Primary exact matrix audit for EXP-001049.

This is an inference boundary for the central A-context needed by EXP-001048.
The finite witness is not identified with an actual Q3 operator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-central-context-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[safe(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inf_norm(matrix: sp.Matrix) -> sp.Rational:
    return max((sum(abs(matrix[row, column]) for column in range(matrix.cols)) for row in range(matrix.rows)), default=sp.Rational(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    base = sp.Integer(fixture["base"])
    quartic_power = int(fixture["quartic_power"])
    cubic_power = int(fixture["cubic_power"])
    dimension = int(fixture["dimension"])
    n_values = [int(value) for value in fixture["n_values"]]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("schema", manifest["schema"].endswith("/1.0"), manifest["schema"], ".../1.0", "provenance")
    check("exploration", manifest["exploration_id"] == "EXP-001049", manifest["exploration_id"], "EXP-001049", "provenance")
    check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("fixture dimensions", dimension == 3 and base >= 2 and quartic_power == 4 and cubic_power == 3, [dimension, base, quartic_power, cubic_power], "3,>=2,4,3", "fixture")
    shift = sp.Matrix([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    rows: list[dict[str, Any]] = []
    for n in n_values:
        energy = sp.diag(1, base ** (quartic_power * n), base ** (2 * quartic_power * n))
        factor = sp.diag(1, base ** (cubic_power * n), base ** (2 * cubic_power * n))
        inverse_factor = sp.diag(1, base ** (-cubic_power * n), base ** (-2 * cubic_power * n))
        check(f"fractional power identity n={n}", factor**quartic_power == energy**cubic_power, factor**quartic_power, energy**cubic_power, "derivation")
        D = shift * factor
        right_one = D * inverse_factor
        left_one = inverse_factor * D
        central = factor * D * inverse_factor
        ordinary = D
        right_norm = inf_norm(right_one)
        left_norm = inf_norm(left_one)
        central_norm = inf_norm(central)
        ordinary_norm = inf_norm(ordinary)
        expected_left = base ** (-cubic_power * n)
        expected_central = base ** (2 * cubic_power * n)
        expected_ordinary = base ** (cubic_power * n)
        check(f"right one-sided norm n={n}", right_norm == 1, right_norm, 1, "one-sided")
        check(f"left one-sided norm n={n}", left_norm == expected_left and left_norm <= 1, left_norm, expected_left, "one-sided")
        check(f"central context norm n={n}", central_norm == expected_central, central_norm, expected_central, "central")
        check(f"ordinary context norm n={n}", ordinary_norm == expected_ordinary, ordinary_norm, expected_ordinary, "central")
        check(f"central amplification n={n}", central_norm > 1, central_norm, ">1", "central")
        rows.append({"n": n, "right_one_norm": right_norm, "left_one_norm": left_norm, "central_norm": central_norm, "ordinary_norm": ordinary_norm, "one_sided_bound": right_norm <= 1 and left_norm <= 1, "central_bound_failed": central_norm > 1})

    check("central family grows", rows[-1]["central_norm"] > rows[0]["central_norm"], [rows[0]["central_norm"], rows[-1]["central_norm"]], "strict growth", "central")
    check("scope boundary", manifest["scope"]["central_context_inference_refuted"] is True and manifest["scope"]["actual_q3_central_context_proved"] is False, manifest["scope"], "inference refuted/actual open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS",
        "passed": passed, "total": passed, "failed": 0, "assertions": audit, "family_rows": rows,
        "derived": {
            "base": base, "quartic_power": quartic_power, "cubic_power": cubic_power, "dimension": dimension,
            "right_one_factor_norm": rows[0]["right_one_norm"], "left_one_factor_norm": rows[0]["left_one_norm"],
            "central_context_norm": rows[0]["central_norm"], "ordinary_context_norm": rows[0]["ordinary_norm"],
            "family_central_norms": [row["central_norm"] for row in rows],
            "one_sided_bounds_uniform_in_fixture": all(row["one_sided_bound"] for row in rows),
            "central_context_inference_from_one_sided_failed": False,
            "ordinary_context_inference_from_one_sided_failed": False,
            "actual_q3_factor_identification": False, "actual_q3_central_context_proved": False,
            "actual_q3_history_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY Q3-CENTRAL-CONTEXT-BOUNDARY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
