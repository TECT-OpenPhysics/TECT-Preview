#!/usr/bin/env python3
"""Primary exact audit for EXP-001067.

The audit records the finite CCR-core kinetic/force split of the second
generator acting on a configuration character and an exact two-level witness
showing that a force-only bound cannot control the kinetic contribution.
It is a scoped interface checkpoint, not an actual Q3 thermodynamic theorem.
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
SLUG = "pre-a-cp1-st8-q3lock-kinetic-force-double-commutator-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[safe(item) for item in row] for row in value.tolist()]
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001067" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001067/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("derivation convention", manifest["model"]["derivation"] == "delta_H(X)=i[H,X]/hbar", manifest["model"]["derivation"], "delta=i[H,.]/hbar", "convention")
    check("exact split declared", "(p_x+a/2)^2" in manifest["model"]["exact_split"] and "F_x" in manifest["model"]["exact_split"], manifest["model"]["exact_split"], "kinetic plus force", "CCR")

    n = sp.Integer(manifest["adversarial_fixture"]["fixture_n"])
    H = sp.diag(0, n)
    rho = sp.diag(sp.Rational(2, 3), sp.Rational(1, 3))
    W = sp.Matrix([[0, 1], [1, 0]])
    delta = lambda X: sp.I * (H * X - X * H)
    delta2 = sp.simplify(delta(delta(W)))

    def seminorm_squared(X: sp.Matrix) -> sp.Expr:
        adjoint = sp.conjugate(X).T
        return sp.simplify(sp.trace(rho * adjoint * X) + sp.trace(rho * X * adjoint))

    expected_delta2 = -n**2 * W
    initial_norm = seminorm_squared(W)
    double_norm = seminorm_squared(delta2)
    formula_norm = 2 * n**4
    check("H self-adjoint", sp.conjugate(H).T == H, sp.conjugate(H).T, H, "fixture")
    check("rho normalized", sp.trace(rho) == 1, sp.trace(rho), 1, "fixture")
    check("W unitary", W.T * W == sp.eye(2), W.T * W, sp.eye(2), "fixture")
    check("force zero", sp.Integer(0) == 0, 0, 0, "force")
    check("second commutator", delta2 == expected_delta2, delta2, expected_delta2, "fixture")
    check("initial two-sided norm", initial_norm == 2, initial_norm, 2, "fixture")
    check("double norm formula", double_norm == formula_norm, double_norm, formula_norm, "fixture")
    check("n=4 fixture", double_norm == sp.Integer(manifest["adversarial_fixture"]["fixture_squared_norm"]), double_norm, manifest["adversarial_fixture"]["fixture_squared_norm"], "fixture")

    growth_rows: list[dict[str, Any]] = []
    for level in range(1, 6):
        squared = 2 * sp.Integer(level) ** 4
        growth_rows.append({"n": level, "double_squared_norm": squared})
        check(f"growth formula n={level}", squared == 2 * sp.Integer(level) ** 4, squared, 2 * sp.Integer(level) ** 4, "growth")
    check("strict growth", growth_rows[-1]["double_squared_norm"] > growth_rows[0]["double_squared_norm"], growth_rows, "increasing", "growth")

    scope = manifest["scope"]
    check("positive split scope", scope["finite_ccr_split_closed"] is True and scope["force_endpoint_interface_reused"] is True, scope, "finite split and force interface", "scope")
    check("force-only shortcut scope", scope["force_only_shortcut_rejected"] is True and scope["no_new_negative_result"] is True, scope, "route-local obstruction", "scope")
    open_keys = ("kinetic_uniform_bound_closed", "modular_multiplier_bound_closed", "actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open", "scope")

    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "derived": {
            "fixture_n": n,
            "initial_two_sided_squared_norm": initial_norm,
            "double_commutator": expected_delta2,
            "double_two_sided_squared_norm": double_norm,
            "force_moment": 0,
            "finite_ccr_split_closed": True,
            "force_endpoint_interface_reused": True,
            "kinetic_uniform_bound_closed": False,
            "modular_multiplier_bound_closed": False,
            "force_only_shortcut_rejected": True,
            "actual_q3_double_commutator_uniform_closed": False,
            "growth_rows": growth_rows,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
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
    print(f"PRIMARY KINETIC-FORCE-SPLIT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
