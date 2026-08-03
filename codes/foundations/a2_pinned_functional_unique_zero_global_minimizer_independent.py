#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-157 minimizer bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A2-FULL-PRODUCTION-WELLPOSED"
RESULT_ID = "A2-PINNED-FUNCTIONAL-UNIQUE-ZERO-GLOBAL-MINIMIZER"
LEDGER_ID = "R-157"
SLUG = "pinned-functional-unique-zero-global-minimizer"
SCHEMA = f"tect/a2-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A2_STATUS = REPO / "claims/A2-FULL-PRODUCTION-WELLPOSED/status.json"
BACKEND = REPO / "codes/foundations/n001_variational_backend.py"
SCOPE = {
    "pinned_a1_p1_functional": True,
    "a2_fixed_torus_continuum_h2": True,
    "eta_shell_zero": True,
    "unconstrained_linear_field_space": True,
    "unique_zero_global_minimizer": True,
    "unique_zero_critical_point": True,
    "nonzero_stationary_or_metastable_equilibrium_exclusion": True,
    "canonical_gradient_flow_exponential_l2_decay": True,
    "physical_vacuum_selection": False,
    "historical_backend": False,
    "a7_covariance_normal_composite": False,
    "fixed_norm_or_charge_constraint": False,
    "chemical_potential_modified_model": False,
    "compact_cp2_target": False,
    "conserved_or_alternative_dynamics": False,
    "alternative_parameter_or_functional_branches": False,
}
NO_OVERCLAIM = (
    "R-157 applies only to the unconstrained hash-pinned P1/A2 classical functional on the fixed torus "
    "with eta_shell=0 and to its canonical L2 gradient flow. It makes Psi=0 the unique critical point "
    "and global minimizer and forces exponential L2 decay in that flow. It is not a physical-vacuum "
    "theorem; it does not apply to the historical backend, signed A7 stochastic composite, fixed-norm/charge "
    "or compact-target constraints, chemical-potential or conserved dynamics, other parameters/functionals, "
    "or general nonequilibrium transients."
)


def frac(value: Any) -> F:
    return F(str(value))


def det2(matrix: list[list[F]]) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def det3(matrix: list[list[F]]) -> F:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def stringify(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(stringify(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []

    def check(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": stringify(actual), "expected": stringify(expected)})

    manifest = json.loads(A1.read_text(encoding="utf-8"))
    status = json.loads(A2_STATUS.read_text(encoding="utf-8"))
    p = manifest["parameters"]
    check("authority", "A1 authority", manifest["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", manifest["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    check("authority", "A2 is conditional continuum theorem", status["tier"] == "T6" and "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL" in status["hypotheses"], [status["tier"], status["hypotheses"]], "T6 with named hypothesis")
    check("authority", "backend hash", sha256(BACKEND) == manifest["production_reference_backend"]["sha256"], sha256(BACKEND), manifest["production_reference_backend"]["sha256"])

    r, z, y = frac(p["r"]), frac(p["Z"]), frac(p["Y"])
    lam, gamma = frac(p["lambda"]), frac(p["gamma"])
    shell = r - z * z / (4 * y)
    expected_shell = F(26000000000947494031, 10**20)
    check("linear", "shell minimum", shell == expected_shell and shell > 0, shell, expected_shell)
    check("linear", "shell minimizer is admissible", -z / (2 * y) > 0, -z / (2 * y), ">0")

    m = [[F(1, 10), -F(1, 20), -F(1, 20)], [-F(1, 20), F(13, 100), -F(1, 20)], [-F(1, 20), -F(1, 20), F(17, 100)]]
    lower = F(7, 250)
    shifted = [[m[i][j] - (lower if i == j else 0) for j in range(3)] for i in range(3)]
    minors = [shifted[0][0], det2([row[:2] for row in shifted[:2]]), det3(shifted)]
    expected_minors = [F(9, 125), F(1211, 250000), F(89, 31250000)]
    check("linear", "independent Sylvester test", minors == expected_minors and all(item > 0 for item in minors), minors, expected_minors)

    total = shell + lower
    rho_star = -3 * lam / (4 * gamma)
    gap = total / 2 - 3 * lam * lam / (32 * gamma)
    expected_gap = F(719818750025582338837, 5400000000000000000000)
    check("potential", "vertex", rho_star == F(43, 216), rho_star, F(43, 216))
    check("potential", "exact gap", gap == expected_gap, gap, expected_gap)
    check("potential", "strict positivity", gap > 0, gap, ">0")
    check("potential", "one-eighth corollary", gap > F(1, 8), gap - F(1, 8), ">0")
    # Coefficient matching verifies q(rho)=gap+(gamma/6)(rho-rho*)^2.
    lhs = [total / 2, lam / 4, gamma / 6]
    rhs = [gap + gamma * rho_star * rho_star / 6, -gamma * rho_star / 3, gamma / 6]
    check("potential", "completion coefficient parity", lhs == rhs, lhs, rhs)

    cjj, cjk, ckk = frac(p["cJJ"]), frac(p["cJK"]), frac(p["cKK"])
    alpha, beta = frac(p["alpha_X"]), frac(p["beta_X"])
    denom = frac(p["M_X"]) ** 2 + frac(p["classii_mass_regularizer"])
    a = cjj * alpha * alpha / denom
    b = cjk * alpha * beta / denom
    c = ckk * beta * beta / denom
    determinant = a * c - b * b
    check("classii", "input coefficient determinant", cjj * ckk - cjk * cjk == F(1, 50), cjj * ckk - cjk * cjk, F(1, 50))
    check("classii", "scaled coefficient positive definite", a > 0 and determinant > 0, [a, determinant], ">0")
    check("classii", "eta shell zero", frac(p["eta_shell"]) == 0, frac(p["eta_shell"]), 0)

    # Independently expand det R_theta at theta=0,1 and its coefficients.
    # R11=a-theta*b, R12=b+theta*(b-c)/2, R22=c*(1+theta).
    det_coefficients = [
        a * c - b * b,
        a * c - b * c - b * (b - c),
        -b * c - (b - c) * (b - c) / 4,
    ]
    expected_det_coefficients = [F(9 * 128, 10240000) / (denom * denom), F(9 * 128, 10240000) / (denom * denom), -F(9 * 81, 10240000) / (denom * denom)]
    check("classii-ray", "radial determinant coefficients", det_coefficients == expected_det_coefficients, det_coefficients, expected_det_coefficients)
    det_at_zero = det_coefficients[0]
    det_at_one = sum(det_coefficients)
    check("classii-ray", "radial matrix positive on unit theta interval", a - b > 0 and det_at_zero > 0 and det_at_one > 0, [a - b, det_at_zero, det_at_one], ">0; concave determinant has positive endpoints")
    radial_gap = total - lam * lam / (4 * gamma)
    expected_radial_gap = F(2101675000076747016511, 8100000000000000000000)
    check("critical-point", "exact radial derivative gap", radial_gap == expected_radial_gap and radial_gap > F(1, 4), radial_gap, expected_radial_gap)

    source = BACKEND.read_text(encoding="utf-8")
    required_source_tokens = [
        '0.5 * float(params["r"])',
        '0.25 * float(params["lambda"])',
        '(float(params["gamma"]) / 6.0)',
        '0.5 * a_jj',
        'b_jk *',
        '0.5 * c_kk',
    ]
    check("backend", "energy normalization tokens", all(token in source for token in required_source_tokens), required_source_tokens, "all present")
    check("verdict", "unique minimizer implication", gap > 0, "F[Psi]>=g||Psi||2; F[0]=0", "Psi=0 only")
    check("verdict", "unique critical point implication", radial_gap > 0, "<DF(Psi),Psi>>=kappa||Psi||2", "Psi=0 only")
    check("dynamics", "canonical gradient flow exponential decay implication", radial_gap > 0, "d||Psi||2/dt<=-2 kappa||Psi||2", "||Psi(t)||2<=exp(-2 kappa t)||Psi(0)||2")
    check("boundary", "physical-vacuum firewall", True, "pinned functional selection is not empirical model selection", "excluded")
    check("boundary", "non-equilibrium firewall", True, "time-dependent non-equilibrium structures not excluded", "open")
    check("boundary", "signed A7 firewall", True, "covariance-normal counterterm not covered", "excluded")

    failures = [row for row in rows if row["status"] != "PASS"]
    if failures:
        raise AssertionError(json.dumps(failures, indent=2))
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "derived": {"shell_minimum": shell, "internal_lower": lower, "total_mass": total, "rho_star": rho_star, "strict_l2_gap": gap, "strict_radial_derivative_gap": radial_gap, "classii_determinant": determinant, "classii_radial_determinant_coefficients": det_coefficients},
        "authority_hashes": {"A1_manifest": sha256(A1), "A2_status": sha256(A2_STATUS), "backend": sha256(BACKEND)},
        "assertions": rows,
        "summary": {"passed": len(rows), "failed": 0, "total": len(rows)},
        "independence": "standard-library Fraction reconstruction; does not import the primary certificate",
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(args.output, payload)
    print(f"{RESULT_ID} independent: {len(rows)}/{len(rows)} PASS; g={gap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
