#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001049."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-central-context-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"
Matrix = list[list[F]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [[sum((left[row][inner] * right[inner][column] for inner in range(3)), F(0)) for column in range(3)] for row in range(3)]


def diag(values: list[F]) -> Matrix:
    return [[values[row] if row == column else F(0) for column in range(3)] for row in range(3)]


def norm_inf(matrix: Matrix) -> F:
    return max((sum((abs(value) for value in row), F(0)) for row in matrix), default=F(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    base = F(fixture["base"])
    qpow = int(fixture["quartic_power"])
    cpower = int(fixture["cubic_power"])
    ns = [int(value) for value in fixture["n_values"]]
    shift: Matrix = [[F(0), F(0), F(0)], [F(1), F(0), F(0)], [F(0), F(1), F(0)]]
    rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001049" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001049/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("declared abstraction", "not identified" in manifest["input_boundary"]["interpretation"], manifest["input_boundary"]["interpretation"], "not identified", "scope")
    for n in ns:
        energy = diag([F(1), base ** (qpow * n), base ** (2 * qpow * n)])
        factor = diag([F(1), base ** (cpower * n), base ** (2 * cpower * n)])
        inverse = diag([F(1), F(1, base ** (cpower * n)), F(1, base ** (2 * cpower * n))])
        check(f"power identity n={n}", multiply(multiply(multiply(factor, factor), factor), factor) == multiply(multiply(energy, energy), energy), True, True, "derivation")
        D = multiply(shift, factor)
        right = multiply(D, inverse)
        left = multiply(inverse, D)
        central = multiply(multiply(factor, D), inverse)
        ordinary = D
        right_norm, left_norm = norm_inf(right), norm_inf(left)
        central_norm, ordinary_norm = norm_inf(central), norm_inf(ordinary)
        expected_left = F(1, base ** (cpower * n))
        expected_central = base ** (2 * cpower * n)
        expected_ordinary = base ** (cpower * n)
        check(f"right norm n={n}", right_norm == 1, right_norm, 1, "one-sided")
        check(f"left norm n={n}", left_norm == expected_left and left_norm <= 1, left_norm, expected_left, "one-sided")
        check(f"central norm n={n}", central_norm == expected_central, central_norm, expected_central, "central")
        check(f"ordinary norm n={n}", ordinary_norm == expected_ordinary, ordinary_norm, expected_ordinary, "central")
        check(f"central amplification n={n}", central_norm > 1, central_norm, ">1", "central")
        rows.append({"n": n, "right_one_norm": right_norm, "left_one_norm": left_norm, "central_norm": central_norm, "ordinary_norm": ordinary_norm, "one_sided_bound": right_norm <= 1 and left_norm <= 1, "central_bound_failed": central_norm > 1})

    check("strict central growth", rows[0]["central_norm"] < rows[-1]["central_norm"], [rows[0]["central_norm"], rows[-1]["central_norm"]], "increasing", "central")
    check("history gate remains open", manifest["scope"]["actual_q3_history_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS",
        "passed": passed, "total": passed, "failed": 0, "assertions": checks, "family_rows": rows,
        "derived": {
            "base": base, "quartic_power": qpow, "cubic_power": cpower,
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
    print(f"INDEPENDENT Q3-CENTRAL-CONTEXT-BOUNDARY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
