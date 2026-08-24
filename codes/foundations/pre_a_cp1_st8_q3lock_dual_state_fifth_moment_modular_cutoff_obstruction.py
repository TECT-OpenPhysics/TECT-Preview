#!/usr/bin/env python3
"""Primary exact audit for the EXP-001079 dual-state cutoff witness."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-dual-state-fifth-moment-modular-cutoff-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-"
    "gibbs-weighted-noncommutative-moment-transfer-obstruction-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-26-primary-{SLUG}"
    / "primary.json"
)


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001079" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001079/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001078" and previous["scope"]["finite_gibbs_obstruction_closed"] is True, previous["exploration_id"], "EXP-001078 finite Gibbs obstruction", "authority")
    check("Gibbs witness declared", "exp(-beta" in manifest["matrix_family"]["gibbs_identity"] and "L^6" in manifest["matrix_family"]["state"], manifest["matrix_family"], "finite-temperature Gibbs state", "model")
    check("cutoff declared", "1_[k<=2]" in manifest["matrix_family"]["cutoff"] and "diag(0,1)" in manifest["matrix_family"]["cutoff"], manifest["matrix_family"]["cutoff"], "exact spectral projection", "model")

    exponent = int(fixture["gibbs_ratio_exponent"])
    cutoff = sp.Integer(fixture["cutoff_R"])
    values = [sp.Integer(value) for value in fixture["L_values"]]
    derived_reference: list[sp.Rational] = []
    derived_dual: list[sp.Rational] = []
    derived_tail: list[sp.Rational] = []
    derived_relative: list[sp.Rational] = []
    for index, L in enumerate(values, start=1):
        denominator = L**exponent + 1
        k = sp.diag(1, L)
        B = sp.Matrix([[0, 1], [1, 0]])
        rho = sp.diag(sp.Rational(L**exponent, denominator), sp.Rational(1, denominator))
        P = sp.diag(1, 0)
        Q = sp.diag(0, 1)
        identity = sp.eye(2)
        check(f"L range {index}", L > cutoff, L, f">{cutoff}", "family")
        check(f"state positive trace {index}", rho[0, 0] > 0 and rho[1, 1] > 0 and sp.trace(rho) == 1, rho, "positive trace-one", "state")
        check(f"Gibbs ratio {index}", sp.factor(rho[1, 1] / rho[0, 0]) == sp.Rational(1, L**exponent), rho[1, 1] / rho[0, 0], sp.Rational(1, L**exponent), "state")
        check(f"finite beta {index}", sp.log(L) > 0 and sp.Rational(exponent, 1) * sp.log(L) / (L - 1) > 0, L, "beta>0", "state")
        check(f"cutoff projection {index}", P * P == P and Q * Q == Q and P + Q == identity and P * k == P, [P * P, Q * Q, P + Q, P * k], "P,Q spectral projections", "cutoff")
        check(f"relative bound right {index}", sp.simplify((k.inv() * B.T * B).eigenvals()) == {sp.Rational(1, L): 1, sp.Integer(1): 1}, (k.inv() * B.T * B).eigenvals(), "{1,1/L}", "relative")
        check(f"relative bound left {index}", sp.simplify((B.T * k.inv() * B).eigenvals()) == {sp.Integer(1): 1, sp.Rational(1, L): 1}, (B.T * k.inv() * B).eigenvals(), "{1,1/L}", "relative")
        reference = sp.factor(sp.trace(rho * (k**5)))
        dual = sp.factor(sp.trace(B * rho * B.T * (k**5)))
        tail = sp.factor(sp.trace(rho * B.T * Q * B))
        check(f"reference fifth moment {index}", reference == sp.factor(L**5 * (L + 1) / denominator), reference, sp.factor(L**5 * (L + 1) / denominator), "moment")
        check(f"dual fifth moment {index}", dual == sp.factor((L**11 + 1) / denominator), dual, sp.factor((L**11 + 1) / denominator), "dual")
        check(f"reference ceiling {index}", reference < sp.Rational(3, 2), reference, "<3/2", "moment")
        check(f"dual growth {index}", dual > L**4, dual, f">{L**4}", "dual")
        check(f"opposite tail identity {index}", tail == sp.factor(L**6 / denominator), tail, sp.factor(L**6 / denominator), "tail")
        check(f"opposite tail floor {index}", tail > sp.Rational(1, 2), tail, ">1/2", "tail")
        derived_reference.append(reference)
        derived_dual.append(dual)
        derived_tail.append(tail)
        derived_relative.append(sp.Integer(1))

    scope = manifest["scope"]
    check("finite dual-state obstruction", scope["finite_dual_state_obstruction_closed"] is True and scope["one_sided_moment_shortcut_refuted"] is True, {key: scope[key] for key in ("finite_dual_state_obstruction_closed", "one_sided_moment_shortcut_refuted")}, "route-local obstruction", "scope")
    open_keys = tuple(key for key, value in scope.items() if isinstance(value, bool) and key.endswith("_closed") and key not in ("finite_dual_state_obstruction_closed", "one_sided_moment_shortcut_refuted", "conditional_dual_tail_theorem_identified"))
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual Q3 and QFT gates open", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-FIFTH-MOMENT-MODULAR-CUTOFF-OBSTRUCTION",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "L_values": values,
            "gibbs_ratio_exponent": exponent,
            "cutoff_R": cutoff,
            "reference_moment": derived_reference,
            "dual_moment": derived_dual,
            "opposite_tail": derived_tail,
            "relative_squared_norm": derived_relative,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY DUAL-STATE FIFTH-MOMENT CUTOFF OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
