#!/usr/bin/env python3
"""Primary exact finite Gibbs-invariance fixture for EXP-001065."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-gibbs-invariance-conditional-os-intertwiner-manifest.json"
PRIOR = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-mixture-seminorm-orbit-contract-stress-test-manifest.json"
OS_ROUTE = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-finite-gibbs-invariance-conditional-os-intertwiner/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    os_route = json.loads(OS_ROUTE.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    fixture = manifest["fixture"]
    q = sp.Rational(fixture["boltzmann_ratio"])
    w0 = sp.simplify(1 / (1 + q))
    w1 = sp.simplify(q / (1 + q))
    rho = sp.diag(w0, w1)
    U = sp.diag(1, -1)
    X = sp.Matrix([[sp.Rational(value) for value in row] for row in fixture["observable"]])
    evolved = sp.conjugate(U).T * X * U
    identity = sp.eye(2)

    def seminorm_squared(matrix: sp.Matrix) -> sp.Expr:
        adjoint = sp.conjugate(matrix).T
        return sp.simplify(sp.trace(rho * adjoint * matrix) + sp.trace(rho * matrix * adjoint))

    initial = seminorm_squared(X)
    evolved_norm = seminorm_squared(evolved)
    gap = sp.factor(evolved_norm - initial)

    check("identity", manifest["exploration_id"] == "EXP-001065" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001065/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("prior identity", prior["exploration_id"] == "EXP-001064", prior["exploration_id"], "EXP-001064")
    check("OS embedding remains missing", os_route["exploration_id"] == "EXP-000800" and "not yet" in os_route["hamiltonian_identification_boundary"]["missing_identification"], os_route["hamiltonian_identification_boundary"]["missing_identification"], "missing finite Hamiltonian embedding")
    check("Boltzmann normalization", w0 + w1 == 1, w0 + w1, 1)
    check("Gibbs weights", [w0, w1] == [sp.Rational(value) for value in fixture["weights"]], [w0, w1], fixture["weights"])
    check("unitarity", sp.conjugate(U).T * U == identity, sp.conjugate(U).T * U, identity)
    check("Gibbs commutation", rho * U - U * rho == sp.zeros(2), rho * U - U * rho, sp.zeros(2))
    check("sign conjugation", evolved == sp.Matrix([[1, -2], [-3, 4]]), evolved, fixture["evolved_observable"])
    check("initial norm", initial == sp.Rational(fixture["initial_squared_norm"]), initial, fixture["initial_squared_norm"])
    check("evolved norm", evolved_norm == sp.Rational(fixture["evolved_squared_norm"]), evolved_norm, fixture["evolved_squared_norm"])
    check("orbit gap", gap == sp.Rational(fixture["orbit_gap"]), gap, fixture["orbit_gap"])
    check("finite isometry", evolved_norm == initial, [initial, evolved_norm], "equal")

    hypotheses = manifest["conditional_os_transfer"]["hypotheses"]
    check("conditional hypotheses", len(hypotheses) == 4, len(hypotheses), 4)
    scope = manifest["scope"]
    check("finite scope", scope["finite_gibbs_isometry_closed"] is True and scope["conditional_os_transfer_statement_closed"] is True, scope, "finite theorem plus conditional transfer")
    open_keys = ("finite_hamiltonian_os_embedding_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_orbit_bound_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GIBBS-INVARIANCE-CONDITIONAL-OS-INTERTWINER",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "boltzmann_ratio": str(q),
            "weights": [str(w0), str(w1)],
            "gibbs_commutes_with_unitary": True,
            "initial_squared_norm": str(initial),
            "evolved_squared_norm": str(evolved_norm),
            "orbit_gap": str(gap),
            "finite_gibbs_isometry_closed": True,
            "conditional_os_transfer_statement_closed": True,
            "finite_hamiltonian_os_embedding_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-GIBBS-INVARIANCE PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
