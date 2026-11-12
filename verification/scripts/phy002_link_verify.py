#!/usr/bin/env python3
"""Exact local charge/number diagnostic; NOT a full GFT or TECT theorem.

python -X utf8 verification/scripts/phy002_link_verify.py --out claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-phy002/link.json
Optional: --source-cache internal/source-cache/tect-phy-002
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/physical-candidates/TECT-PHY-002-link-v1.json"
# Immutable input identities, not derived mathematical constants.
CONTRACT_SHA = "1b848a35dc2e4c1102b246c3afc71929fb52cc4cd320ac9794e820efaf4ba683"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert sha(CONTRACT) == CONTRACT_SHA
    admission = ROOT / "strategy/physical-candidates/TECT-PHY-002-admission-v1.json"
    assert sha(admission) == contract["admission_sha256"]
    assert sha(ROOT / contract["tect_input"]["path"]) == contract["tect_input"]["sha256"]
    source_verified = False
    if args.source_cache:
        assert sha(args.source_cache / contract["source"]["cache_file"]) == contract["source"]["sha256"]
        source_verified = True

    a, b, m = s.symbols("a b m", positive=True)
    phi = s.symbols("phi", real=True)
    sigma = a * (s.cosh(m * phi) + s.I * s.sinh(m * phi))
    derivative = s.diff(sigma, phi)
    number = s.simplify(s.expand_complex(s.conjugate(sigma) * sigma))
    charge = s.simplify(-s.I * (s.conjugate(sigma) * derivative - sigma * s.conjugate(derivative)) / 2)
    x, y = s.re(sigma), s.im(sigma)
    real_charge = s.simplify(x * s.diff(y, phi) - y * s.diff(x, phi))
    residual = s.simplify(s.diff(sigma, phi, 2) - m**2 * sigma)
    half_norm = number / 2
    derivative_half_norm = s.simplify(s.diff(half_norm, phi))
    second_at_zero = s.simplify(s.diff(half_norm, phi, 2).subs(phi, 0))
    # Independent analytic test oracles, not inputs used to build the witness.
    checks = {
        "reduced_equality_residual_zero": residual == 0,
        "number_formula": s.simplify(number - a**2 * s.cosh(2*m*phi)) == 0,
        "charge_formula": s.simplify(charge - a**2*m) == 0,
        "real_component_convention": s.simplify(charge - real_charge) == 0,
        "charge_constant_in_reduced_law": s.diff(charge, phi) == 0,
        "half_norm_derivative": s.simplify(derivative_half_norm - a**2*m*s.sinh(2*m*phi)) == 0,
        "half_norm_not_constant_locally": second_at_zero.is_positive is True,
    }

    def q_at(z: s.Expr, dz: s.Expr) -> s.Expr:
        return s.simplify(-s.I * (s.conjugate(z)*dz - z*s.conjugate(dz)) / 2)

    n_at = s.simplify(s.conjugate(a)*a)
    q1, q2 = q_at(a, s.I*b), q_at(a, 2*s.I*b)
    checks.update({
        "same_amplitude_two_velocities": n_at == a**2,
        "distinct_charges_at_same_amplitude": s.simplify(q2-q1).is_positive is True,
        "first_initial_charge": s.simplify(q1-a*b) == 0,
        "second_initial_charge": s.simplify(q2-2*a*b) == 0,
    })
    # Hostile substitutions target convention, observable and local-limit errors.
    mutations = {
        "reversed_charge_sign": s.simplify(-charge-real_charge) != 0,
        "missing_half_in_charge": s.simplify(2*charge-real_charge) != 0,
        "number_mistaken_for_constant_charge": s.diff(number, phi) != 0,
        "stationary_point_mistaken_for_constant_function": derivative_half_norm.subs(phi, 0) == 0 and second_at_zero.is_positive is True,
        "same_number_forces_same_charge": s.simplify(q2-q1) != 0,
        "oscillatory_wrong_sign_law": s.simplify(s.diff(sigma, phi, 2)+m**2*sigma) != 0,
    }
    assert all(checks.values()), checks
    assert all(mutations.values()), mutations
    report = {
        "schema": "tect/phy002-link-run/1.0",
        "status": "PASS_SCOPED_DIAGNOSTIC",
        "claim_bearing": False,
        "active_gate_change": False,
        "new_result_id": None,
        "contract_sha256": sha(CONTRACT),
        "script_sha256": sha(Path(__file__)),
        "source_sha256": contract["source"]["sha256"],
        "source_bytes_verified_this_run": source_verified,
        "sympy_version": s.__version__,
        "checks": checks,
        "rejected_mutations": mutations,
        "derived": {
            "sigma": str(sigma), "residual": str(residual), "number": str(number),
            "charge": str(charge), "half_norm_derivative": str(derivative_half_norm),
            "half_norm_second_derivative_at_zero": str(second_at_zero),
            "initial_charges": [str(q1), str(q2)],
        },
        "scope": "One fixed spin, local effective Cauchy data; exact algebra of Eq64 and the equality diagnostic for approximate Eq66. Not all microscopic equations, an exact global coherent state or an error estimate for nonzero interactions.",
        "finding": "A fixed nonzero normalization cannot identify amplitude number/2 with the relational phase charge on this effective phase space. The reduced-law example also separates changing number from constant phase charge.",
        "non_claims": "No universal map no-go, physical-state counterexample, inherited R158 result, physical Pre-A, spacetime, gravity, QFT, continuum or TOE. No Lean proof."
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=True)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "checks": len(checks), "hostile_mutations": len(mutations), "source_verified": source_verified}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
