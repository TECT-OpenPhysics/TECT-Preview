#!/usr/bin/env python3
"""Primary exact scalar obstruction for EXP-001127.

The declared cosine cutoff is exactly zero on the tail sector q >= 2L.  The
quartic Q3 bond tail times its force has degree seven, while a local quartic
energy to the 3/4 power has graph degree three.  Fraction arithmetic checks
the polynomial identity, the exact lower bound, the power-count exponent and
the separated lambda=0 boundary.  This is a route-local operator-norm no-go;
it does not replace the kinetic operator by a multiplication operator.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-local-tail-force-a34-operator-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}/primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def bond(c: Fraction, lam: Fraction, q: Fraction, v: Fraction) -> Fraction:
    d = q - v
    return c * d * d / 2 + lam * d * d * (q * q + v * v) / 4


def force(c: Fraction, lam: Fraction, q: Fraction, v: Fraction) -> Fraction:
    d = q - v
    return c * d + lam * d * (2 * q * q - q * v + v * v) / 2


def mixed_expanded(c: Fraction, lam: Fraction, q: Fraction) -> Fraction:
    return c * c * q**3 / 2 + 3 * c * lam * q**5 / 4 + lam * lam * q**7 / 4


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001127" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001127/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("negative authority", manifest["negative_ids"] == ["NG-2026-08-25-PRE-A-ST8-Q3LOCK-LOCAL-QUARTIC-TAIL-FORCE-A34-OPERATOR-FACTORIZATION"], manifest["negative_ids"], "one route-local no-go", "scope")
    c = Fraction(1, 1)
    lam = Fraction(1, 10)
    gamma = Fraction(1, 20)
    L = Fraction(1, 1)
    check("positive quartic parameters", c > 0 and lam > 0 and gamma > 0 and L > 0, [c, lam, gamma, L], "positive", "model")
    q_values = [Fraction(4), Fraction(8), Fraction(16), Fraction(32)]
    ratio_rows: list[dict[str, Any]] = []
    for q in q_values:
        check(f"tail sector q={q}", q >= 2 * L, q, f">={2 * L}", "cutoff")
        b = bond(c, lam, q, Fraction(0))
        f = force(c, lam, q, Fraction(0))
        expanded = mixed_expanded(c, lam, q)
        mixed = b * f
        check(f"polynomial identity q={q}", mixed == expanded, mixed, expanded, "exact polynomial")
        leading = lam * lam * q**7 / 4
        check(f"leading lower bound q={q}", mixed >= leading, mixed, f">={leading}", "quartic tail")
        energy = 1 + gamma * q**4
        ratio_fourth = mixed**4 / energy**3
        lower_fourth = (lam * lam / 4) ** 4 * q**16 / (1 + gamma) ** 3
        check(f"graph ratio lower bound q={q}", ratio_fourth >= lower_fourth, ratio_fourth, f">={lower_fourth}", "graph power")
        ratio_rows.append({"q": q, "bond": b, "force": f, "mixed": mixed, "energy": energy, "ratio_fourth": ratio_fourth, "lower_fourth": lower_fourth})
    check("ratio grows on declared sequence", all(ratio_rows[index + 1]["ratio_fourth"] > ratio_rows[index]["ratio_fourth"] for index in range(len(ratio_rows) - 1)), [r["ratio_fourth"] for r in ratio_rows], "strictly increasing", "unboundedness diagnostic")

    lam_zero = Fraction(0)
    q_zero = Fraction(16)
    mixed_zero = bond(c, lam_zero, q_zero, Fraction(0)) * force(c, lam_zero, q_zero, Fraction(0))
    check("lambda zero degree boundary", mixed_zero == c * c * q_zero**3 / 2, mixed_zero, c * c * q_zero**3 / 2, "boundary")
    check("quartic power deficit", Fraction(7) - 4 * Fraction(3, 4) == 4, Fraction(7) - 4 * Fraction(3, 4), 4, "power count")
    check("quadratic power deficit", Fraction(3) - 4 * Fraction(3, 4) == 0, Fraction(3) - 4 * Fraction(3, 4), 0, "lambda zero boundary")
    scope = manifest["scope"]
    check("scope firewall", scope["quartic_lambda_positive_operator_route_rejected"] and scope["state_weighted_modular_route_open"] and scope["direct_d_delta_d_route_open"] and not scope["common_alpha_closed"], scope, "named route only", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-TAIL-FORCE-A34-OPERATOR-OBSTRUCTION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "ratio_rows": ratio_rows,
            "quartic_degree": 7,
            "energy_three_quarter_degree": 3,
            "quartic_ratio_degree": 4,
            "lambda_zero_degree": 3,
            "quartic_operator_route_rejected": True,
            "lambda_zero_subcase_open": True,
            "state_weighted_route_open": True,
        },
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY LOCAL-TAIL-FORCE-A34 PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
