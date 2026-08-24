#!/usr/bin/env python3
"""Primary exact matrix audit for EXP-001047.

The finite shift family isolates the repeated A-power transport missing from
the one-factor Q3 graph estimate.  It is an inference boundary, not an actual
Q3 operator theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-repeated-factor-transport-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
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


Matrix = list[list[Fraction]]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return [[sum((left[row][inner] * right[inner][column] for inner in range(size)), Fraction(0)) for column in range(size)] for row in range(size)]


def diagonal(values: list[Fraction]) -> Matrix:
    return [[values[row] if row == column else Fraction(0) for column in range(len(values))] for row in range(len(values))]


def inf_norm(matrix: Matrix) -> Fraction:
    return max((sum((abs(value) for value in row), Fraction(0)) for row in matrix), default=Fraction(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    base = int(fixture["base"])
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
    check("exploration", manifest["exploration_id"] == "EXP-001047", manifest["exploration_id"], "EXP-001047", "provenance")
    check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("dimension", dimension == 3, dimension, 3, "fixture")
    check("base", base >= 2, base, ">=2", "fixture")
    check("power ladder", quartic_power == 4 and cubic_power == 3, [quartic_power, cubic_power], [4, 3], "fixture")

    shift: Matrix = [[Fraction(0), Fraction(0), Fraction(0)], [Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0)]]
    rows: list[dict[str, Any]] = []
    for n in n_values:
        energy_ratio = base ** (quartic_power * n)
        energy = [Fraction(1), Fraction(energy_ratio), Fraction(energy_ratio**2)]
        factor = [Fraction(1), Fraction(base ** (cubic_power * n)), Fraction(base ** (2 * cubic_power * n))]
        inverse_factor = [Fraction(1), Fraction(1, factor[1]), Fraction(1, factor[2])]
        inverse_repeated = [Fraction(1), Fraction(1, factor[1] * factor[1]), Fraction(1, factor[2] * factor[2])]
        check(f"energy fractional-power identity n={n}", factor[1] ** quartic_power == energy[1] ** cubic_power and factor[2] ** quartic_power == energy[2] ** cubic_power, [factor[1] ** quartic_power, factor[2] ** quartic_power], [energy[1] ** cubic_power, energy[2] ** cubic_power], "derivation")
        q = matmul(shift, diagonal(factor))
        right_one = matmul(q, diagonal(inverse_factor))
        left_one = matmul(diagonal(inverse_factor), q)
        repeated = matmul(matmul(q, q), diagonal(inverse_repeated))
        right_norm = inf_norm(right_one)
        left_norm = inf_norm(left_one)
        repeated_norm = inf_norm(repeated)
        expected_left = Fraction(1, base ** (cubic_power * n))
        expected_repeated = Fraction(base ** (cubic_power * n))
        check(f"right one-factor norm n={n}", right_norm == 1, right_norm, 1, "one-factor")
        check(f"left one-factor norm n={n}", left_norm == expected_left and left_norm <= 1, left_norm, expected_left, "one-factor")
        check(f"repeated product norm n={n}", repeated_norm == expected_repeated, repeated_norm, expected_repeated, "repeat")
        check(f"repeated amplification n={n}", repeated_norm > 1, repeated_norm, ">1", "repeat")
        rows.append({"n": n, "energy": energy, "factor": factor, "right_one_norm": right_norm, "left_one_norm": left_norm, "repeated_norm": repeated_norm, "one_factor_bound": right_norm <= 1 and left_norm <= 1, "repeated_bound_one_failed": repeated_norm > 1})

    check("family grows", rows[-1]["repeated_norm"] > rows[0]["repeated_norm"], [rows[0]["repeated_norm"], rows[-1]["repeated_norm"]], "strict growth", "repeat")
    check("scope boundary", manifest["scope"]["actual_q3_factor_identification"] is False and manifest["scope"]["higher_moment_or_A_power_transport_closed"] is False, manifest["scope"], "actual Q3 and transport open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "family_rows": rows,
        "derived": {
            "base": base,
            "quartic_power": quartic_power,
            "cubic_power": cubic_power,
            "dimension": dimension,
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
    print(f"PRIMARY Q3-REPEATED-FACTOR-TRANSPORT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
