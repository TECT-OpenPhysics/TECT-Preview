#!/usr/bin/env python3
"""Independent exact Fraction audit for EXP-001047.

This lane rebuilds the three-by-three shift arithmetic without importing the
primary implementation.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-repeated-factor-transport-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"
Matrix = list[list[F]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def multiply(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((a[i][k] * b[k][j] for k in range(3)), F(0)) for j in range(3)] for i in range(3)]


def diag(values: list[F]) -> Matrix:
    return [[values[i] if i == j else F(0) for j in range(3)] for i in range(3)]


def norm_inf(matrix: Matrix) -> F:
    return max((sum((abs(value) for value in row), F(0)) for row in matrix), default=F(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    base = int(fixture["base"])
    qpow = int(fixture["quartic_power"])
    cpower = int(fixture["cubic_power"])
    ns = [int(value) for value in fixture["n_values"]]
    shift: Matrix = [[F(0), F(0), F(0)], [F(1), F(0), F(0)], [F(0), F(1), F(0)]]
    rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001047" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001047/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("declared abstraction", "not identified" in manifest["input_boundary"]["interpretation"], manifest["input_boundary"]["interpretation"], "not identified", "scope")
    for n in ns:
        ratio = base ** (qpow * n)
        energy = [F(1), F(ratio), F(ratio * ratio)]
        factor = [F(1), F(base ** (cpower * n)), F(base ** (2 * cpower * n))]
        inv_factor = [F(1), F(1, factor[1]), F(1, factor[2])]
        inv_repeat = [F(1), F(1, factor[1] ** 2), F(1, factor[2] ** 2)]
        check(f"power identity n={n}", factor[1] ** qpow == energy[1] ** cpower and factor[2] ** qpow == energy[2] ** cpower, [factor[1] ** qpow, factor[2] ** qpow], [energy[1] ** cpower, energy[2] ** cpower], "derivation")
        q = multiply(shift, diag(factor))
        right = multiply(q, diag(inv_factor))
        left = multiply(diag(inv_factor), q)
        repeated = multiply(multiply(q, q), diag(inv_repeat))
        right_norm = norm_inf(right)
        left_norm = norm_inf(left)
        repeated_norm = norm_inf(repeated)
        expected_left = F(1, base ** (cpower * n))
        expected_repeated = F(base ** (cpower * n))
        check(f"right norm n={n}", right_norm == F(1), right_norm, F(1), "one-factor")
        check(f"left norm n={n}", left_norm == expected_left and left_norm <= F(1), left_norm, expected_left, "one-factor")
        check(f"repeated norm n={n}", repeated_norm == expected_repeated, repeated_norm, expected_repeated, "repeat")
        check(f"amplification n={n}", repeated_norm > F(1), repeated_norm, ">1", "repeat")
        rows.append({"n": n, "energy": energy, "factor": factor, "right_one_norm": right_norm, "left_one_norm": left_norm, "repeated_norm": repeated_norm, "one_factor_bound": right_norm <= 1 and left_norm <= 1, "repeated_bound_one_failed": repeated_norm > 1})

    check("strict family growth", rows[0]["repeated_norm"] < rows[-1]["repeated_norm"], [rows[0]["repeated_norm"], rows[-1]["repeated_norm"]], "increasing", "repeat")
    check("history gate remains open", manifest["scope"]["actual_q3_history_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": checks,
        "family_rows": rows,
        "derived": {
            "base": base,
            "quartic_power": qpow,
            "cubic_power": cpower,
            "right_one_factor_norm": rows[0]["right_one_norm"],
            "left_one_factor_norm": rows[0]["left_one_norm"],
            "repeated_product_norm": rows[0]["repeated_norm"],
            "family_repeated_norms": [row["repeated_norm"] for row in rows],
            "one_factor_bounds_uniform_in_fixture": all(row["one_factor_bound"] for row in rows),
            "repeated_product_bound_from_one_factor_inference": False,
            "actual_q3_factor_identification": False,
            "higher_moment_or_A_power_transport_closed": False,
            "actual_q3_history_closed": False,
            "common_alpha_closed": False
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST)
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["scope"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT Q3-REPEATED-FACTOR-TRANSPORT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
