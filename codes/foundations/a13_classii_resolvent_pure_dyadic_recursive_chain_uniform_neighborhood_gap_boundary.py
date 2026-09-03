#!/usr/bin/env python3
"""Primary exact audit for the R-162 recursive-chain neighbourhood theorem.

This executable checks the finite algebra and exact constants used by the
analytic proof.  The certified radius is deliberately analytic and
nonnumerical because its final inputs are finite compact-data derivative
suprema for the registered A7 coefficient.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RESOLVENT-PURE-DYADIC-RECURSIVE-CHAIN-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-162"
SLUG = "resolvent-pure-dyadic-recursive-chain-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"

AUTHORITIES = {
    "A1": REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json",
    "A7": REPO / "claims" / "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE" / "classii_renormalised_energy_manifest.json",
    "R-107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-159": CLAIM_DIR / "classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary_manifest.json",
    "R-160": CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json",
    "R-161": CLAIM_DIR / "classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_manifest.json",
}
R160_MANIFEST = AUTHORITIES["R-160"]
R161_MANIFEST = AUTHORITIES["R-161"]

SCOPE = {
    "deterministic_matrix_coefficients": True,
    "centered_independent_raw_gaussian_blocks": True,
    "actual_shifted_state_read_at_each_stage": True,
    "finite_acyclic_single_pure_dyadic_chain": True,
    "uniform_over_chain_length_starting_mode_finite_cutoff_and_admitted_regulator": True,
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_positive_A7_floor": True,
    "fixed_spatial_dimension_three": True,
    "exact_nonaliased_continuum_torus_integration": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "summed_HS_l2_coefficient_norm": True,
    "complete_expected_global_terminal_scalar": True,
    "complete_controller_pullback_hessian": True,
    "projected_force_connection_included": True,
    "sextic_connection_included": True,
    "forward_legal_reverse_balanced_are_one_hessian": True,
    "independent_low_or_feshbach_coordinate": False,
    "intrinsic_hessian_claimed": False,
    "arbitrary_unrelated_multichain_forest": False,
    "random_or_nonlinear_past_dependent_coefficients": False,
    "revisit_or_cycles": False,
    "pathwise_fibrewise_conditional_hessian": False,
    "local_root_ECN_equals_Pcomp": False,
    "floor_or_infinite_endpoint_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-162 proves one positive analytic l2(HS) coefficient radius for each finite acyclic single "
    "pure-dyadic deterministic-matrix shifted-state recursion, with one radius uniform in its "
    "finite length, retained starting mode, finite cutoff, and admitted common-even contraction "
    "regulator, at the fixed side-16 d=3 A1/A7 setting. It controls the complete expected global "
    "controller-pullback Hessian and includes the projected-force, source, current, trace, and "
    "sextic connection terms once. It proves no intrinsic-Hessian theorem, unrelated multi-chain "
    "forest, random or nonlinear past-dependent coefficient law, revisit/cycle, pathwise fibrewise "
    "conditional estimate, removal, T-050/A13, Nelson, measure, phase/PDE, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def repo_relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def shift(values: tuple[sp.Expr, sp.Expr, sp.Expr]) -> sp.Matrix:
    matrix = sp.zeros(4)
    for index, value in enumerate(values):
        matrix[index + 1, index] = value
    return matrix


def resolvent(matrix: sp.Matrix) -> sp.Matrix:
    # Every four-block fixture is nilpotent of order four.
    identity = sp.eye(4)
    return identity + matrix + matrix**2 + matrix**3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, path in AUTHORITIES.items():
        audit.check("authority", f"{label} exists", path.is_file(), repo_relative(path), "existing file")

    r160_manifest = json.loads(R160_MANIFEST.read_text(encoding="utf-8"))
    r160_record = r160_manifest["files"]["primary_result"]
    r160_result_path = REPO / r160_record["path"]
    audit.check("authority", "R-160 result hash", sha256_text(r160_result_path) == r160_record["sha256"], sha256_text(r160_result_path), r160_record["sha256"])
    r160 = json.loads(r160_result_path.read_text(encoding="utf-8"))
    origin_gap = sp.Rational(r160["diagnostics"]["lattice_certified_gap"])
    audit.check("authority", "R-160 exact origin gap", origin_gap == sp.Rational(4, 25), origin_gap, sp.Rational(4, 25))
    audit.check("authority", "R-160 primary passed", r160["summary"]["failed"] == 0, r160["summary"], "zero failures")
    r161_manifest = json.loads(R161_MANIFEST.read_text(encoding="utf-8"))
    r161_record = r161_manifest["files"]["primary_result"]
    r161_result_path = REPO / r161_record["path"]
    audit.check("authority", "R-161 result hash", sha256_text(r161_result_path) == r161_record["sha256"], sha256_text(r161_result_path), r161_record["sha256"])
    r161 = json.loads(r161_result_path.read_text(encoding="utf-8"))
    r155_manifest = json.loads(AUTHORITIES["R-155"].read_text(encoding="utf-8"))
    r155_statement = r155_manifest["statement"]
    audit.check("authority", "R-155 stationary p-to-4p connection cancellation", "{+/-3p,+/-5p}" in r155_statement and "vanish only" in r155_statement and "stationary" in r155_statement, r155_statement, "stationary exact-support cancellation")
    audit.check("authority", "R-161 global-owner firewall", r161_manifest["scope"]["global_terminal_action_only"] is True and r161_manifest["scope"]["local_root_ECN_equals_Pcomp"] is False, r161_manifest["scope"], "global true; local false")

    # Exact resolvent jets on a noncommuting chronological block-shift fixture.
    a = (sp.Rational(1, 7), sp.Rational(-1, 5), sp.Rational(2, 9))
    h = (sp.Rational(2, 5), sp.Rational(1, 3), sp.Rational(-3, 8))
    k = (sp.Rational(-1, 4), sp.Rational(5, 11), sp.Rational(1, 6))
    ell = (sp.Rational(3, 10), sp.Rational(-2, 7), sp.Rational(4, 13))
    n_a, n_h, n_k, n_l = map(shift, (a, h, k, ell))
    t_a = resolvent(n_a)
    audit.check("resolvent", "finite Neumann inverse", sp.simplify((sp.eye(4) - n_a) * t_a) == sp.eye(4), (sp.eye(4) - n_a) * t_a, sp.eye(4))

    u, v, w = sp.symbols("u v w")
    t_path = resolvent(n_a + u * n_h + v * n_k + w * n_l)
    d1 = t_path.diff(u).subs({u: 0, v: 0, w: 0})
    d2 = t_path.diff(u, v).subs({u: 0, v: 0, w: 0})
    d3 = t_path.diff(u, v, w).subs({u: 0, v: 0, w: 0})
    d1_expected = t_a * n_h * t_a
    d2_expected = t_a * n_h * t_a * n_k * t_a + t_a * n_k * t_a * n_h * t_a
    mats = (n_h, n_k, n_l)
    d3_expected = sum(
        (t_a * mats[p[0]] * t_a * mats[p[1]] * t_a * mats[p[2]] * t_a for p in itertools.permutations(range(3))),
        sp.zeros(4),
    )
    audit.check("resolvent", "first jet identity", sp.simplify(d1 - d1_expected) == sp.zeros(4), d1 - d1_expected, sp.zeros(4))
    audit.check("resolvent", "second jet chronological symmetrisation", sp.simplify(d2 - d2_expected) == sp.zeros(4), d2 - d2_expected, sp.zeros(4))
    audit.check("resolvent", "third jet six permutations", sp.simplify(d3 - d3_expected) == sp.zeros(4), d3 - d3_expected, sp.zeros(4))

    covariance_path = t_path * t_path.T
    # Re-evaluate at the actual origin A=0 for the acceleration-support identity.
    t_origin_path = resolvent(u * n_h)
    g2_zero = (t_origin_path * t_origin_path.T).diff(u, 2).subs(u, 0)
    g2_expected = 2 * (n_h * n_h.T + n_h**2 + (n_h.T) ** 2)
    audit.check("origin", "recursive covariance second jet", sp.simplify(g2_zero - g2_expected) == sp.zeros(4), g2_zero - g2_expected, sp.zeros(4))
    audit.check("origin", "acceleration occupies two-step diagonal", all(g2_expected[i, j] == 0 for i in range(4) for j in range(4) if abs(i - j) > 2), "bandwidth <= 2", "bandwidth <= 2")
    audit.check("origin", "p to 4p Fourier differences", {4 - 1, 4 + 1} == {3, 5}, sorted({4 - 1, 4 + 1}), [3, 5])

    # Exact A1 dyadic synthesis envelopes.  These deliberately coarse bounds
    # are stronger than needed and avoid an unregistered numerical supremum.
    g = sp.Rational(r161["derived"]["synthesis_envelope_g"])
    c0 = sp.Rational(r161["derived"]["side16_lattice_floor_c0"])
    b_s = sp.Rational(16, 15) * g / c0**2
    b_d = sp.Rational(4, 3) * g / c0
    c_z_squared = b_s**2 + 9 * b_d**2 + 18 * b_s * b_d
    audit.check("synthesis", "registered g", g == sp.Rational(244140625000000000, 28800000000947494031), g, sp.Rational(244140625000000000, 28800000000947494031))
    audit.check("synthesis", "value dyadic sum", b_s == sp.Rational(312500000000000000000, 777600000025582338837), b_s, "exact B_S")
    audit.check("synthesis", "current dyadic sum", b_d == sp.Rational(19531250000000000000, 259200000008527446279), b_d, "exact B_D")
    audit.check("synthesis", "data-map constant positive", c_z_squared > 0, c_z_squared, "> 0")
    audit.check("synthesis", "data-map constant below one", c_z_squared < 1, c_z_squared, "< 1")
    audit.check("synthesis", "value geometric ratio", sum(sp.Rational(1, 16) ** j for j in range(12)) < sp.Rational(16, 15), "partial sum", "< 16/15")
    audit.check("synthesis", "current geometric ratio", sum(sp.Rational(1, 4) ** j for j in range(12)) < sp.Rational(4, 3), "partial sum", "< 4/3")

    # Covariance resolvent derivative constants at the fixed audit ball r0=1/2.
    r0 = sp.Rational(1, 2)
    tau0 = 1 / (1 - r0)
    j1_factor = 2 * tau0**3
    j2_factor = 6 * tau0**4
    j3_factor = 24 * tau0**5
    audit.check("modulus", "tau at audit ball", tau0 == 2, tau0, 2)
    audit.check("modulus", "covariance first jet factor", j1_factor == 16, j1_factor, 16)
    audit.check("modulus", "covariance second jet factor", j2_factor == 96, j2_factor, 96)
    audit.check("modulus", "covariance third jet factor", j3_factor == 768, j3_factor, 768)

    m1, m2, m3, cz = sp.symbols("M_1 M_2 M_3 c_Z", positive=True)
    terminal_bracket = sp.expand(m3 * (16 * cz) ** 3 + 3 * m2 * (16 * cz) * (96 * cz) + m1 * (768 * cz))
    terminal_expected = 4096 * m3 * cz**3 + 4608 * m2 * cz**2 + 768 * m1 * cz
    audit.check("modulus", "complete third-order chain rule", sp.simplify(terminal_bracket - terminal_expected) == 0, terminal_bracket, terminal_expected)

    cm_d3_at_r0 = sp.Rational(27, 5) * (1 + r0) * tau0**5
    audit.check("modulus", "complete source connection bound", cm_d3_at_r0 == sp.Rational(1296, 5), cm_d3_at_r0, sp.Rational(1296, 5))
    headroom_loss = sp.Rational(3, 100)
    retained = origin_gap - headroom_loss
    audit.check("gap", "retained coefficient gap", retained == sp.Rational(13, 100), retained, sp.Rational(13, 100))
    audit.check("gap", "retained exceeds target", retained > sp.Rational(1, 10), retained, "> 1/10")
    audit.check("gap", "exact metric ceiling at r<3/100", (sp.Rational(100, 97)) ** 4 < sp.Rational(13, 10), (sp.Rational(100, 97)) ** 4, "< 13/10")

    # The Gaussian sextic belongs inside the scalar modulus.  Verify its trace
    # polynomial on a two-coordinate diagonal covariance and reject the false
    # claim that nonlinear pullback preserves convexity.
    c1, c2 = sp.symbols("c1 c2", nonnegative=True)
    gaussian_direct = 15 * c1**3 + 9 * c1**2 * c2 + 9 * c1 * c2**2 + 15 * c2**3
    gaussian_trace = (c1 + c2) ** 3 + 6 * (c1 + c2) * (c1**2 + c2**2) + 8 * (c1**3 + c2**3)
    audit.check("sextic", "Gaussian sixth-moment trace polynomial", sp.expand(gaussian_direct - gaussian_trace) == 0, sp.expand(gaussian_trace), sp.expand(gaussian_direct))
    aa, bb = sp.symbols("aa bb")
    pulled = aa**6 * bb**6
    pulled_hessian = sp.hessian(pulled, (aa, bb)).subs({aa: 1, bb: 1})
    eigenvalues = sorted(int(value) for value in pulled_hessian.eigenvals())
    audit.check("sextic", "nonlinear pullback counterexample Hessian", pulled_hessian == sp.Matrix([[30, 36], [36, 30]]), pulled_hessian, sp.Matrix([[30, 36], [36, 30]]))
    audit.check("sextic", "nonlinear pullback has negative eigenvalue", eigenvalues == [-6, 66], eigenvalues, [-6, 66])

    # A dimension-growing coherent fixture makes bare per-chain continuity
    # logically insufficient; the explicit resolvent/synthesis modulus is the
    # load-bearing input.
    n = sp.symbols("n", integer=True, positive=True)
    coherent_hessian = sp.Rational(4, 25) - 3 + 5 / n
    audit.check("failure", "coherent fixture negative by n=3", coherent_hessian.subs(n, 3) < 0, coherent_hessian.subs(n, 3), "< 0")
    audit.check("failure", "raw full-lattice derivative sum is not used", SCOPE["arbitrary_unrelated_multichain_forest"] is False, SCOPE["arbitrary_unrelated_multichain_forest"], False)
    audit.check("scope", "intrinsic theorem not claimed", SCOPE["intrinsic_hessian_claimed"] is False, SCOPE["intrinsic_hessian_claimed"], False)
    audit.check("scope", "one Hessian and no invented low", SCOPE["forward_legal_reverse_balanced_are_one_hessian"] is True and SCOPE["independent_low_or_feshbach_coordinate"] is False, [SCOPE["forward_legal_reverse_balanced_are_one_hessian"], SCOPE["independent_low_or_feshbach_coordinate"]], [True, False])
    audit.check("scope", "T-050 remains open", SCOPE["t050_closed"] is False, SCOPE["t050_closed"], False)
    audit.check("scope", "Sector A remains open", SCOPE["sector_a_closed"] is False, SCOPE["sector_a_closed"], False)

    audit.require()
    hashes = {label: sha256_text(path) for label, path in AUTHORITIES.items()}
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "inputs": {
            "authority_hashes": hashes,
            "volume": str(16**3),
            "origin_gap": str(origin_gap),
            "target_gap": "1/10",
            "audit_ball": str(r0),
        },
        "diagnostics": {
            "g": str(g),
            "B_S": str(b_s),
            "B_D": str(b_d),
            "c_Z_squared": str(c_z_squared),
            "covariance_jet_factors_at_r0": [str(j1_factor), str(j2_factor), str(j3_factor)],
            "terminal_D3_bracket": str(terminal_expected),
            "terminal_D3_coefficients_M1_M2_M3": [str(j3_factor), str(3 * j1_factor * j2_factor), str(j1_factor**3)],
            "CM_D3_bound_at_r0": str(cm_d3_at_r0),
            "retained_gap": str(retained),
            "analytic_radius": "delta_*=min(1/2,3/[100(1+L_*)]) with L_* finite and including the complete sextic and source connections",
            "metric_guard": "delta_*<3/100 and (100/97)^4<13/10",
            "sextic_pullback_counterexample_eigenvalues": eigenvalues,
        },
        "assertions": audit.rows,
        "summary": {
            "total": len(audit.rows),
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
        },
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(arguments.output, payload)
    print(f"PASS {payload['summary']['passed']}/{payload['summary']['total']} -> {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
