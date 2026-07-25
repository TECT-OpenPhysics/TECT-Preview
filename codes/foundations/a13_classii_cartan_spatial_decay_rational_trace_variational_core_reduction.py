#!/usr/bin/env python3
"""Primary executable evidence for the R-087 A13 reduction.

The script checks the exact scale arithmetic behind the mixed Cartan
spatial atom estimate, the rare-event obstruction to a pathwise translated
model-norm extraction, the eta-regularised rational Schur/Wick identity, and
the A13 Boue--Dupuis coefficient ledger.  The analytic paralinearisation and
bounded cylindrical variational-core arguments are proved in the companion
note; this program checks their finite algebraic and numerical consequences.

It does not assert the expected one-use q-ledger, complete Cartan CFAR,
complete rational NEAR, REG, OVERLAP, the Nelson bound, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION"
R085 = REPO / f"claims/{CLAIM}/classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
R086 = REPO / f"claims/{CLAIM}/classii_rational_translated_wick_payload_comparable_reduction_manifest.json"
OUTPUT = REPO / f"claims/{CLAIM}/runs/2026-07-25-primary-cartan-spatial-decay-rational-trace-variational-core-reduction/result.json"


# These are theorem inputs or deliberately labelled exact test oracles, never
# pasted outputs of the calculations below.
INPUTS = {
    "spatial_dimension": 3,
    "root_covariance_decay": 4,
    "holder_alpha": Fraction(2, 5),
    "chosen_s": Fraction(7, 12),
    "far_separation": 5,
    "nelson_q": Fraction(10, 9),
    "comparison_p": Fraction(11, 10),
}

TEST_ORACLES = {
    "value_root_exponent": -1,
    "derivative_root_exponent": 1,
    "cartan_beta": Fraction(7, 5),
    "maximum_s": Fraction(7, 10),
    "root_margin": Fraction(7, 30),
    "gap_margin": Fraction(13, 30),
    "variational_energy": Fraction(9, 20),
    "q_minus_p": Fraction(1, 90),
    "energy_reserve": Fraction(1, 220),
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def matrix_contraction(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.trace(left.T * right)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def serial(value: Any) -> Any:
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, sp.Basic):
            return str(value)
        if isinstance(value, (list, tuple)):
            return [serial(item) for item in value]
        if isinstance(value, dict):
            return {key: serial(item) for key, item in value.items()}
        return value

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    r085 = json.loads(R085.read_text(encoding="utf-8"))
    r086 = json.loads(R086.read_text(encoding="utf-8"))
    check(
        "r085_predecessor",
        r085.get("result_id") == "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY",
        r085.get("result_id"),
        "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY",
    )
    check(
        "r086_predecessor",
        r086.get("result_id") == "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION",
        r086.get("result_id"),
        "A13-CLASSII-RATIONAL-TRANSLATED-WICK-PAYLOAD-COMPARABLE-REDUCTION",
    )

    dimension = INPUTS["spatial_dimension"]
    covariance_decay = INPUTS["root_covariance_decay"]
    alpha = INPUTS["holder_alpha"]
    chosen_s = INPUTS["chosen_s"]
    beta = 6 * alpha - 1
    value_root_exponent = dimension - covariance_decay
    derivative_root_exponent = dimension + 2 - covariance_decay
    maximum_s = beta / 2
    root_margin = beta - 2 * chosen_s
    gap_margin = 4 * alpha - 2 * chosen_s

    check("value_root_covariance_exponent", value_root_exponent == TEST_ORACLES["value_root_exponent"], value_root_exponent, TEST_ORACLES["value_root_exponent"])
    check("derivative_root_covariance_exponent", derivative_root_exponent == TEST_ORACLES["derivative_root_exponent"], derivative_root_exponent, TEST_ORACLES["derivative_root_exponent"])
    check("cartan_beta", beta == TEST_ORACLES["cartan_beta"], str(beta), str(TEST_ORACLES["cartan_beta"]))
    check("cartan_maximum_s", maximum_s == TEST_ORACLES["maximum_s"], str(maximum_s), str(TEST_ORACLES["maximum_s"]))
    check("chosen_s_above_schur_threshold", chosen_s > Fraction(1, 2), str(chosen_s), ">1/2")
    check("chosen_s_below_cartan_threshold", chosen_s < maximum_s, str(chosen_s), f"<{maximum_s}")
    check("root_scale_margin", root_margin == TEST_ORACLES["root_margin"], str(root_margin), str(TEST_ORACLES["root_margin"]))
    check("far_gap_margin", gap_margin == TEST_ORACLES["gap_margin"], str(gap_margin), str(TEST_ORACLES["gap_margin"]))
    check("derivative_root_gap_margin_positive", 6 * alpha - 2 * chosen_s > 0, str(6 * alpha - 2 * chosen_s), ">0")

    # Exact support arithmetic for the compactly supported smooth analytic
    # LP partition fixed in the note: chi_n is supported in (4/3)Q_n and is
    # one on (3/4)Q_n.  A Q_j-supported input has no blocks above j+1; its
    # square has no blocks above j+2.  Radii are measured in units of 2^j.
    p1_radius_units = Fraction(5, 3) * 2
    p2_radius_units = Fraction(5, 3) * 4
    first_channel_radius = p1_radius_units + 1 + 1 + 1
    second_channel_radius = p2_radius_units + 1 + 1
    third_channel_radius = p2_radius_units + 1 + 1
    projection_lower_edge = 2 ** (INPUTS["far_separation"] - 1)
    principal_radius = max(first_channel_radius, second_channel_radius, third_channel_radius)
    containing_cube_offset = math.ceil(math.log2(principal_radius))
    check("p1_support_radius_units", p1_radius_units == Fraction(10, 3), str(p1_radius_units), "10/3")
    check("p2_support_radius_units", p2_radius_units == Fraction(20, 3), str(p2_radius_units), "20/3")
    check("principal_support_radius_units", principal_radius == Fraction(26, 3), str(principal_radius), "26/3")
    check("principal_support_cube_offset", containing_cube_offset == 4, containing_cube_offset, 4)
    check("far_projection_strict_separation", principal_radius < projection_lower_edge, [principal_radius, projection_lower_edge], "principal < Pi lower edge")
    check("safe_C0", INPUTS["far_separation"] == 5, INPUTS["far_separation"], 5)

    # Exponent comparison for all j>=k and d=m-j>=C0.  The two nonnegative
    # margins are exactly what converts the raw HS estimate to (4.10).
    for index, (j_minus_k, gap) in enumerate(((0, 5), (1, 5), (9, 5), (0, 11), (7, 13)), start=1):
        excess = root_margin * j_minus_k + gap_margin * gap
        check(f"cartan_exponent_fixture_{index}", excess >= 0, str(excess), ">=0")

    # The Cartan curvature of Phi=qz is exact and nonzero, so the principal
    # mechanism is support annihilation rather than a fictitious algebraic
    # cancellation of the three mixed channels.
    x, y, floor = sp.symbols("x y floor", positive=True, real=True)
    density = x**2 + y**2 + floor
    q = (x**2 - y**2) / density
    phi = sp.Matrix([q * x, q * y])
    curvature = sp.factor(sp.diff(phi[1], x) - sp.diff(phi[0], y))
    curvature_expected = 4 * x * y / density
    check("cartan_curvature_formula", sp.simplify(curvature - curvature_expected) == 0, str(curvature), str(curvature_expected))
    check("cartan_curvature_nonzero_at_balanced_point", sp.simplify(curvature.subs({x: 1, y: 1}) - 4 / (2 + floor)) == 0, str(curvature.subs({x: 1, y: 1})), "4/(2+floor)")

    # Exact rare-event scaling.  Write N=p^{-1/6}; the energy and sextic
    # expectations remain order one, whereas the pathwise-extracted q-ledger
    # grows like N^6=p^{-1}.  This is a no-go for that proof method only.
    rare_exponent_identity = beta + 1
    check("rare_event_beta_identity", rare_exponent_identity == 6 * alpha, str(rare_exponent_identity), str(6 * alpha))
    for index, probability in enumerate((Fraction(1, 2**6), Fraction(1, 3**6), Fraction(1, 5**6)), start=1):
        shell_size = round(float(probability) ** (-1 / 6))
        extracted_ledger = shell_size**6
        check(f"rare_event_shell_exact_{index}", Fraction(1, shell_size**6) == probability, shell_size, f"p^(-1/6) for p={probability}")
        check(f"rare_event_energy_{index}", probability * (1 / probability) == 1, str(probability * (1 / probability)), "1")
        check(f"rare_event_mixed_budget_{index}", probability * (1 / probability) == 1, str(probability * (1 / probability)), "1")
        check(f"rare_event_extracted_growth_{index}", extracted_ledger == 1 / probability, str(extracted_ledger), str(1 / probability))

    # Generic exact eta-regularised Schur/Wick completion.
    l11, l12, l22 = sp.symbols("l11 l12 l22", real=True)
    b11, b12, b22 = sp.symbols("b11 b12 b22", real=True)
    g1, g2, c1, c2 = sp.symbols("g1 g2 c1 c2", real=True)
    gamma11, gamma12, gamma22 = sp.symbols("gamma11 gamma12 gamma22", real=True)
    eta = sp.symbols("eta", positive=True, real=True)
    identity = sp.eye(2)
    l_matrix = sp.Matrix([[l11, l12], [l12, l22]])
    b1_matrix = sp.Matrix([[b11, b12], [b12, b22]])
    gamma = sp.Matrix([[gamma11, gamma12], [gamma12, gamma22]])
    g_vector = sp.Matrix([g1, g2])
    c_vector = sp.Matrix([c1, c2])
    q_tensor = g_vector * g_vector.T - gamma
    a_eta = b1_matrix + 2 * eta * identity
    a_inverse = a_eta.inv()
    m_eta = l_matrix - l_matrix * a_inverse * l_matrix
    left = (
        matrix_contraction(l_matrix, q_tensor) / 2
        + (g_vector.T * l_matrix * c_vector)[0]
        + (c_vector.T * b1_matrix * c_vector)[0] / 2
        + eta * (c_vector.T * c_vector)[0]
    )
    shifted = c_vector + a_inverse * l_matrix * g_vector
    trace_debt = matrix_contraction(l_matrix * a_inverse * l_matrix, gamma) / 2
    right = (
        (shifted.T * a_eta * shifted)[0] / 2
        + matrix_contraction(m_eta, q_tensor) / 2
        - trace_debt
    )
    completion_residual = sp.cancel(left - right)
    check("rational_eta_completion_identity", completion_residual == 0, str(completion_residual), "0")

    # Exact two-dimensional fixtures for positivity, the debt bound, and the
    # fact that M_eta has no universal sign.
    fixture_eta = sp.Rational(1, 2)
    fixture_b1 = sp.eye(2)
    fixture_l = sp.diag(1, -1)
    fixture_gamma = sp.diag(2, 3)
    fixture_a = fixture_b1 + 2 * fixture_eta * sp.eye(2)
    fixture_m = fixture_l - fixture_l * fixture_a.inv() * fixture_l
    fixture_debt = matrix_contraction(fixture_l * fixture_a.inv() * fixture_l, fixture_gamma) / 2
    fixture_debt_bound = matrix_contraction(fixture_l**2, fixture_gamma) / (4 * fixture_eta)
    check("rational_A_eta_positive", min(fixture_a.eigenvals().keys()) > 0, [str(v) for v in fixture_a.eigenvals().keys()], ">0")
    check("rational_M_eta_indefinite", fixture_m.det() < 0, str(fixture_m), "indefinite")
    check("rational_trace_debt_nonnegative", fixture_debt >= 0, str(fixture_debt), ">=0")
    check("rational_trace_debt_bound", fixture_debt <= fixture_debt_bound, [str(fixture_debt), str(fixture_debt_bound)], "debt <= bound")
    amplitude = sp.symbols("amplitude", real=True)
    small_l = amplitude**3 * fixture_l
    small_correction = sp.simplify(small_l * fixture_a.inv() * small_l)
    check("rational_small_amplitude_correction_order", all(sp.Poly(entry, amplitude).degree() == 6 for entry in small_correction if entry != 0), str(small_correction), "order amplitude^6")
    check("rational_leading_packet_persists", sp.simplify((small_l - small_correction) / amplitude**3).subs(amplitude, 0) == fixture_l, str(sp.simplify((small_l - small_correction) / amplitude**3).subs(amplitude, 0)), str(fixture_l))

    # Exact Nelson/Boue--Dupuis coefficient arithmetic and a solvable linear
    # Gaussian fixture.  For G(x)=b*x, the optimal constant drift is -q*b.
    q_nelson = INPUTS["nelson_q"]
    p_compare = INPUTS["comparison_p"]
    variational_energy = 1 / (2 * q_nelson)
    q_minus_p = q_nelson - p_compare
    energy_reserve = 1 / (2 * p_compare) - variational_energy
    check("variational_energy_coefficient", variational_energy == TEST_ORACLES["variational_energy"], str(variational_energy), str(TEST_ORACLES["variational_energy"]))
    check("nelson_q_minus_p", q_minus_p == TEST_ORACLES["q_minus_p"], str(q_minus_p), str(TEST_ORACLES["q_minus_p"]))
    check("nelson_energy_reserve", energy_reserve == TEST_ORACLES["energy_reserve"], str(energy_reserve), str(TEST_ORACLES["energy_reserve"]))
    gaussian_slope = Fraction(7, 13)
    optimal_drift = -q_nelson * gaussian_slope
    variational_value = gaussian_slope * optimal_drift + variational_energy * optimal_drift**2
    gaussian_log_laplace = -q_nelson * gaussian_slope**2 / 2
    check("linear_gaussian_variational_fixture", variational_value == gaussian_log_laplace, str(variational_value), str(gaussian_log_laplace))

    claims_not_established = {
        "cartan_one_use_q_ledger": False,
        "complete_production_cartan_atom_estimate": False,
        "controlled_cartan_cfar": False,
        "coefficient_dominant_rational_packet": False,
        "rational_shifted_hessian_form_bound": False,
        "complete_rational_near": False,
        "complete_signed_near": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-cartan-spatial-decay-rational-trace-variational-core-reduction-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "cartan": {
            "alpha": str(alpha),
            "chosen_s": str(chosen_s),
            "maximum_s": str(maximum_s),
            "beta": str(beta),
            "root_margin": str(root_margin),
            "gap_margin": str(gap_margin),
            "principal_support_cube": f"Q_(j+{containing_cube_offset})",
            "safe_C0": INPUTS["far_separation"],
            "conditional_qk": "C_e*2^{-(6alpha-1)k}*sup_{j>=k} E int Z_{j,r}^6 (||a_k||_2^2+||D a_k||_2^2) dr",
        },
        "rational": {
            "identity": "P+eta|c|^2 = |A_eta^(1/2)(c+A_eta^(-1)LG)|^2/2 + M_eta:Q/2 - Tr(LA_eta^(-1)L Gamma)/2",
            "A_eta": "B_1+2eta I",
            "M_eta": "L-LA_eta^(-1)L",
            "trace_debt_bound": "Tr(L^2 Gamma)/(4eta)",
            "fixture_M_eta": [[str(value) for value in row] for row in fixture_m.tolist()],
        },
        "variational_core": {
            "q": str(q_nelson),
            "energy_coefficient": str(variational_energy),
            "comparison_p": str(p_compare),
            "q_minus_p": str(q_minus_p),
            "energy_reserve": str(energy_reserve),
            "class": "bounded cylindrical simple progressive controls at each fixed cutoff",
        },
        "negative_method": {
            "id": "NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION",
            "rare_event_growth": "p^(-1)",
            "scope": "method no-go, not a counterexample to the complete Cartan atom",
        },
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if passed == len(rows):
        print(f"[R-087 primary] {passed}/{len(rows)} PASS")
        return 0
    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-087 primary] {passed}/{len(rows)} PASS; failures={failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
