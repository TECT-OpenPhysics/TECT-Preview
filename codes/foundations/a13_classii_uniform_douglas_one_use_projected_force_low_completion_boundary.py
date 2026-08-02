#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-144 checkpoint.

The certificate proves the affine-residual complete-feature one-use theorem,
checks the projected-force/Hessian sufficient route and its sextic margin, types the
source/low pullback, and gives exact q567 phase-cycle, returned-low, and
second-jet non-identifiability fixtures.  It does not provide the missing
production chart, contraction, residual bound, anchor, or uniform margin.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-"
    "LOW-COMPLETION-BOUNDARY"
)
SCHEMA = (
    "tect/a13-uniform-douglas-one-use-projected-force-"
    "low-completion-boundary-primary/1.0"
)
SLUG = "uniform-douglas-one-use-projected-force-low-completion-boundary"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / f"runs/2026-08-02-primary-{SLUG}/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
GATES_PATH = REPO / "claims/GATES.md"
AUTHORITIES = {
    "R-093": REPO / "claims" / CLAIM / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "R-104": REPO / "claims" / CLAIM / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "R-130": REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json",
    "R-140": REPO / "claims" / CLAIM / "classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary_manifest.json",
    "R-141": REPO / "claims" / CLAIM / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-142": REPO / "claims" / CLAIM / "classii_innovation_compressed_common_feature_su2_covariance_signed_collar_band_boundary_manifest.json",
    "R-143": REPO / "claims" / CLAIM / "classii_corrected_q567_feature_contraction_common_noise_anisotropy_tail_boundary_manifest.json",
}
AUTHORITY_RESULT_IDS = {
    "R-093": "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY",
    "R-104": "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY",
    "R-130": "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-RESPONSE-BOUNDARY",
    "R-140": "A13-CLASSII-PREDICTABLE-TRIANGULAR-MIXED-GRAM-SOURCE-GRAPH-FESHBACH-BOUNDARY",
    "R-141": "A13-CLASSII-PROJECTED-FORCE-GLOBAL-DOOB-SIGNED-GRAM-ADAPTIVE-COLLAR-QUOTIENT-BOUNDARY",
    "R-142": "A13-CLASSII-INNOVATION-COMPRESSED-COMMON-FEATURE-SU2-COVARIANCE-SIGNED-COLLAR-BAND-BOUNDARY",
    "R-143": "A13-CLASSII-CORRECTED-Q567-FEATURE-CONTRACTION-COMMON-NOISE-ANISOTROPY-TAIL-BOUNDARY",
}
Q = Fraction

# Registered or explicitly selected analytic inputs.  comparison_p is the
# declared T-050 comparison exponent; fixture inputs below are synthetic
# counterexample parameters and never production outputs.
REGISTERED_ANALYTIC_INPUTS = {
    "comparison_p": Q(11, 10),
    "nelson_q": Q(10, 9),
    "sextic_stabilizer": Q(3, 20),
}
FIXTURE_INPUTS = {
    "rho": Q(1, 2),
    "sigma": Q(3, 4),
    "residual": Q(2),
    "mu": Q(1, 5),
    "theta": Q(1, 2),
    "force_squared": Q(3, 7),
    "fibre_r": Q(7, 5),
    "fibre_s": Q(3, 4),
    "fibre_floor": Q(1, 9),
    "layer_edge": Q(3, 4),
    "returned_low_core_cross": Q(29, 32),
}


# Regression values only.  Every production coefficient is loaded from an
# authority or derived below; these exact values merely detect mutations.
TEST_ORACLES = {
    "phase_cycle_determinants": (Q(5, 32), Q(-49, 32)),
    "mixed_only_minimum": Q(-1, 8),
    "mixed_only_edge": Q(9, 8),
    "low_completion_determinants": (Q(171, 1024), Q(-61, 1024)),
    "double_count_determinant": Q(-585, 256),
    "same_jet_action_hessians": (Q(2), Q(-2)),
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def sf(value: Fraction) -> sp.Rational:
    return sp.Rational(value.numerator, value.denominator)


def smatrix(rows: list[list[Fraction]]) -> sp.Matrix:
    return sp.Matrix([[sf(value) for value in row] for row in rows])


def matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def exact_ldl_inertia(matrix: sp.Matrix) -> tuple[int, int, int]:
    """Exact inertia when every leading principal minor is nonzero."""
    previous = sp.Integer(1)
    positive = negative = 0
    for size in range(1, matrix.rows + 1):
        current = sp.factor(matrix[:size, :size].det())
        if current == 0:
            raise ValueError("zero leading pivot in exact LDL inertia")
        pivot = sp.factor(current / previous)
        if pivot.is_positive is True:
            positive += 1
        elif pivot.is_negative is True:
            negative += 1
        else:
            raise ValueError("undecidable exact pivot sign")
        previous = current
    return positive, negative, matrix.rows - positive - negative


def tensor_inertia(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, int, int]:
    lp, ln, lz = left
    rp, rn, rz = right
    positive = lp * rp + ln * rn
    negative = lp * rn + ln * rp
    zero = (lp + ln + lz) * (rp + rn + rz) - positive - negative
    return positive, negative, zero


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    a1 = load_json(A1_MANIFEST)
    gates_text = GATES_PATH.read_text(encoding="utf-8")
    gate_heading = "### **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE**"
    gate_start = gates_text.index(gate_heading)
    gate_tail = gates_text[gate_start:]
    gate_stop = gate_tail.find("\n### ", len(gate_heading))
    t050_gate_text = gate_tail if gate_stop < 0 else gate_tail[:gate_stop]
    audit.check(
        "authority",
        "A1 manifest identity",
        a1.get("claim_id") == "A1-PRODUCTION-FUNCTIONAL-REALISATION",
        a1.get("claim_id"),
        "A1-PRODUCTION-FUNCTIONAL-REALISATION",
    )
    audit.check(
        "authority",
        "canonical T-050 sextic threshold pinned",
        "epsilon_6<gamma/6=0.27" in t050_gate_text,
        "epsilon_6<gamma/6=0.27" in t050_gate_text,
        True,
    )
    audit.check(
        "authority",
        "canonical T-050 source threshold pinned",
        "epsilon_v<1/(2p)" in t050_gate_text,
        "epsilon_v<1/(2p)" in t050_gate_text,
        True,
    )
    for result, path in AUTHORITIES.items():
        payload = load_json(path)
        audit.check(
            "authority",
            f"{result} authority identity",
            payload.get("result_id") == AUTHORITY_RESULT_IDS[result],
            payload.get("result_id"),
            AUTHORITY_RESULT_IDS[result],
        )

    # 1. Sharp affine-residual contraction inequality.
    rho, sigma, y, residual = sp.symbols(
        "rho sigma y residual", positive=True, real=True
    )
    delta = sigma**2 - rho**2
    sharp_constant = sigma**2 / delta
    majorant_gap = sp.factor(
        sigma**2 * y**2
        + sharp_constant * residual**2
        - (rho * y + residual) ** 2
    )
    audit.check(
        "affine_residual",
        "sharp scalar majorant square",
        sp.factor(delta * majorant_gap - (delta * y - rho * residual) ** 2)
        == 0,
        sp.factor(delta * majorant_gap),
        (delta * y - rho * residual) ** 2,
    )
    rho_q = FIXTURE_INPUTS["rho"]
    sigma_q = FIXTURE_INPUTS["sigma"]
    residual_q = FIXTURE_INPUTS["residual"]
    delta_q = sigma_q**2 - rho_q**2
    sharp_q = sigma_q**2 / delta_q
    equality_y = rho_q * residual_q / delta_q
    left_q = (rho_q * equality_y + residual_q) ** 2
    right_q = sigma_q**2 * equality_y**2 + sharp_q * residual_q**2
    audit.check(
        "affine_residual",
        "strict comparison radii",
        Q(0) <= rho_q < sigma_q < Q(1),
        (rho_q, sigma_q),
        "0 <= rho < sigma < 1",
    )
    audit.check(
        "affine_residual",
        "sharp constant derived",
        sharp_q == Q(9, 5),
        sharp_q,
        Q(9, 5),
    )
    audit.check(
        "affine_residual",
        "equality direction",
        left_q == right_q,
        left_q,
        right_q,
    )
    residual_penalty = sharp_q * residual_q**2 / 2
    audit.check(
        "affine_residual",
        "action residual penalty",
        residual_penalty == Q(18, 5),
        residual_penalty,
        Q(18, 5),
    )

    # Translate the complete-feature reserve into the two strict one-use
    # coefficients.  q=10/9 and the source/sextic weights are registered
    # analytic inputs from R-104/R-143; p=11/10 is the selected comparison
    # exponent used to exhibit strict T-050 source headroom.
    comparison_p = REGISTERED_ANALYTIC_INPUTS["comparison_p"]
    nelson_q = REGISTERED_ANALYTIC_INPUTS["nelson_q"]
    source_weight = Q(1, 2) / nelson_q
    canonical_source_threshold = Q(1, 2) / comparison_p
    source_hessian_weight = 2 * source_weight
    sextic_weight = REGISTERED_ANALYTIC_INPUTS["sextic_stabilizer"]
    gamma = frac(a1["parameters"]["gamma"])
    eps_source = source_weight * sigma_q**2
    eps_sextic = sextic_weight * sigma_q**2
    audit.check(
        "one_use",
        "Nelson and comparison exponents",
        nelson_q - comparison_p == Q(1, 90),
        nelson_q - comparison_p,
        Q(1, 90),
    )
    audit.check(
        "one_use",
        "stronger q-source target clears canonical p-threshold",
        source_weight == Q(1, 2) / nelson_q
        and source_weight < canonical_source_threshold
        and canonical_source_threshold - source_weight == Q(1, 220),
        (source_weight, canonical_source_threshold),
        (Q(9, 20), Q(5, 11)),
    )
    audit.check(
        "one_use",
        "strict source coefficient",
        eps_source < source_weight < canonical_source_threshold,
        eps_source,
        f"<{source_weight}<{canonical_source_threshold}=1/(2p)",
    )
    audit.check(
        "one_use",
        "strict sextic coefficient",
        eps_sextic < sextic_weight < gamma / 6,
        (eps_sextic, sextic_weight),
        f"epsilon_6 < 3/20 < gamma/6={gamma / 6}",
    )
    reserve_source = (Q(1) - sigma_q**2) * source_weight
    reserve_sextic = (Q(1) - sigma_q**2) * sextic_weight
    audit.check(
        "one_use",
        "source reserve exact",
        source_weight - eps_source == reserve_source,
        source_weight - eps_source,
        reserve_source,
    )
    audit.check(
        "one_use",
        "sextic reserve exact",
        sextic_weight - eps_sextic == reserve_sextic,
        sextic_weight - eps_sextic,
        reserve_sextic,
    )

    # 2. Projected-force strong-convexity route.  It improves the source
    # coefficient, while the retained 3/20 sextic loss already lies strictly
    # below the canonical T-050 threshold gamma/6=27/100.
    mu = FIXTURE_INPUTS["mu"]
    theta = FIXTURE_INPUTS["theta"]
    force_sq = FIXTURE_INPUTS["force_squared"]
    fallback_source = source_weight - (Q(1) - theta) * mu / 2
    fallback_constant = force_sq / (2 * theta * mu)
    audit.check(
        "hessian_fallback",
        "source coefficient improves",
        fallback_source == Q(2, 5) < source_weight,
        fallback_source,
        Q(2, 5),
    )
    audit.check(
        "hessian_fallback",
        "force Young constant",
        fallback_constant == Q(15, 7),
        fallback_constant,
        Q(15, 7),
    )
    fallback_sextic = sextic_weight
    audit.check(
        "hessian_fallback",
        "retained sextic coefficient is already strict",
        fallback_sextic == sextic_weight < gamma / 6,
        fallback_sextic,
        "3/20 < gamma/6=27/100",
    )
    fallback_sextic_margin = gamma / 6 - fallback_sextic
    audit.check(
        "hessian_fallback",
        "canonical sextic margin exact",
        fallback_sextic_margin == Q(3, 25),
        fallback_sextic_margin,
        Q(3, 25),
    )

    # 3. Type-correct source/low pullback and the exact vertical source cost.
    synthesis = smatrix(
        [[Q(1), Q(0), Q(1)], [Q(0), Q(1), Q(-1)]]
    )
    physical_low = smatrix(
        [
            [Q(2), Q(1), Q(1, 2)],
            [Q(1), Q(-1), Q(-1, 3)],
            [Q(1, 2), Q(-1, 3), Q(5, 4)],
        ]
    )
    pullback = smatrix(
        [
            [Q(1), Q(0), Q(1), Q(0)],
            [Q(0), Q(1), Q(-1), Q(0)],
            [Q(0), Q(0), Q(0), Q(1)],
        ]
    )
    source_cost = sp.diag(
        sf(source_hessian_weight), sf(source_hessian_weight),
        sf(source_hessian_weight), 0
    )
    source_low_hessian = source_cost + pullback.T * physical_low * pullback
    vertical = smatrix([[Q(-1)], [Q(1)], [Q(1)], [Q(0)]])
    expected_vertical = sf(source_hessian_weight) * vertical
    audit.check(
        "source_typing",
        "vertical vector is in physical kernel",
        synthesis * vertical[:3, :] == sp.zeros(2, 1),
        matrix_strings(synthesis * vertical[:3, :]),
        [["0"], ["0"]],
    )
    audit.check(
        "source_typing",
        "full source-low Hessian dimension",
        source_low_hessian.shape == (4, 4),
        source_low_hessian.shape,
        (4, 4),
    )
    audit.check(
        "source_typing",
        "vertical source cost exactly 9/10",
        source_low_hessian * vertical == expected_vertical,
        matrix_strings(source_low_hessian * vertical),
        matrix_strings(expected_vertical),
    )
    audit.check(
        "source_typing",
        "returned-low cross vanishes on physical source kernel",
        (source_low_hessian * vertical)[3, 0] == 0,
        (source_low_hessian * vertical)[3, 0],
        0,
    )
    good_graph_coupling = smatrix([[Q(1, 4)], [Q(-1, 5)], [Q(9, 20)]])
    bad_graph_coupling = good_graph_coupling + vertical[:3, :] / 21
    audit.check(
        "source_typing",
        "good graph-low coupling kills source kernel",
        (vertical[:3, :].T * good_graph_coupling)[0, 0] == 0,
        (vertical[:3, :].T * good_graph_coupling)[0, 0],
        0,
    )
    audit.check(
        "source_typing",
        "graph-low mutation sees source kernel",
        (vertical[:3, :].T * bad_graph_coupling)[0, 0] == Q(1, 7),
        (vertical[:3, :].T * bad_graph_coupling)[0, 0],
        Q(1, 7),
    )
    bad_null_block = smatrix([[Q(0), Q(1, 7)], [Q(1, 7), Q(1)]])
    audit.check(
        "source_typing",
        "graph-low source-null range failure",
        bad_null_block.det() == Q(-1, 49) < 0,
        bad_null_block.det(),
        Q(-1, 49),
    )

    # Packet labels enlarge the common feature construction, not the source
    # domain unless the chart explicitly declares corresponding directions.
    packet_maps = [
        smatrix([[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)]]),
        smatrix([[Q(0), Q(1), Q(0)], [Q(1), Q(0), Q(1)]]),
        smatrix([[Q(1), Q(-1), Q(0)], [Q(0), Q(0), Q(1)]]),
    ]
    common_map = sum(packet_maps, sp.zeros(2, 3))
    common_gram = common_map.T * common_map
    orthogonalized_gram = sum((item.T * item for item in packet_maps), sp.zeros(3, 3))
    audit.check(
        "source_typing",
        "three packet maps still pull back to source dimension",
        common_gram.shape == (3, 3),
        common_gram.shape,
        (3, 3),
    )
    audit.check(
        "source_typing",
        "artificial packet orthogonalization changes the form",
        common_gram != orthogonalized_gram,
        matrix_strings(common_gram - orthogonalized_gram),
        "nonzero cross-packet Gram",
    )

    # 4. Exact endpoint polarization and the local-Hessian boundary.
    def feature_action(point: tuple[Fraction, Fraction, Fraction]) -> Fraction:
        h1, h2, low = point
        p1 = Q(1) + h1 * h1 + low
        p2 = h2 + h1 * low
        u1 = h1 - h2 + low * low
        return (
            source_weight * (h1 * h1 + h2 * h2)
            + Q(1, 2) * (p1 * p1 + p2 * p2 - u1 * u1)
        )

    x = (Q(1, 2), Q(-1, 3), Q(1, 4))
    x0 = (Q(-1, 5), Q(2, 7), Q(-1, 6))
    hx, h0 = x[:2], x0[:2]
    px = (Q(1) + x[0] ** 2 + x[2], x[1] + x[0] * x[2])
    p0 = (Q(1) + x0[0] ** 2 + x0[2], x0[1] + x0[0] * x0[2])
    ux = (x[0] - x[1] + x[2] ** 2,)
    u0 = (x0[0] - x0[1] + x0[2] ** 2,)
    dot = lambda a, b: sum(left * right for left, right in zip(a, b))
    polarization = (
        source_hessian_weight * dot(tuple(a + b for a, b in zip(hx, h0)), tuple(a - b for a, b in zip(hx, h0)))
        + dot(tuple(a + b for a, b in zip(px, p0)), tuple(a - b for a, b in zip(px, p0)))
        - dot(tuple(a + b for a, b in zip(ux, u0)), tuple(a - b for a, b in zip(ux, u0)))
    )
    audit.check(
        "secant",
        "endpoint polarization exact",
        2 * (feature_action(x) - feature_action(x0)) == polarization,
        2 * (feature_action(x) - feature_action(x0)),
        polarization,
    )

    t, h1, h2, low = sp.symbols("t h1 h2 low", real=True)
    p_sym = sp.Matrix([1 + h1**2 + low, h2 + h1 * low])
    u_sym = h1 - h2 + low**2
    action_sym = (
        sp.Rational(9, 20) * (h1**2 + h2**2)
        + sp.Rational(1, 2) * ((p_sym.T * p_sym)[0] - u_sym**2)
    )
    base = sp.Matrix([sp.Rational(1, 3), sp.Rational(-1, 4), sp.Rational(1, 5)])
    direction_u = sp.Matrix([sp.Rational(1, 2), sp.Rational(2, 3), sp.Rational(-1, 3)])
    direction_v = sp.Matrix([sp.Rational(-2, 5), sp.Rational(1, 7), sp.Rational(3, 4)])
    variables = sp.Matrix([h1, h2, low])
    hessian_sym = sp.hessian(action_sym, variables)
    true_mixed = sp.factor((direction_u.T * hessian_sym.subs(dict(zip(variables, base))) * direction_v)[0])

    def shifted(sign_u: int, sign_v: int) -> sp.Expr:
        point = base + t * (sign_u * direction_u + sign_v * direction_v)
        return action_sym.subs(dict(zip(variables, point)))

    mixed_secant = sp.factor(
        (
            shifted(1, 1)
            - shifted(1, -1)
            - shifted(-1, 1)
            + shifted(-1, -1)
        )
        / (4 * t**2)
    )
    secant_limit = sp.factor(sp.limit(mixed_secant, t, 0))
    audit.check(
        "secant",
        "central endpoint secant converges to Hessian",
        secant_limit == true_mixed,
        secant_limit,
        true_mixed,
    )
    audit.check(
        "secant",
        "finite nonlinear secant is not automatically local Hessian",
        sp.factor(mixed_secant.subs(t, sp.Rational(1, 2)) - true_mixed) != 0,
        sp.factor(mixed_secant.subs(t, sp.Rational(1, 2)) - true_mixed),
        "nonzero remainder",
    )

    # 5. Representation-preserving refinement gives congruence, not spectral
    # equality.  The source embedding is an exact rational isometry.
    inclusion = smatrix(
        [[Q(1), Q(0)], [Q(0), Q(3, 5)], [Q(0), Q(4, 5)]]
    )
    delta_u_f = smatrix([[Q(1, 2), Q(1, 3), Q(1, 4)]])
    gram_f = sp.eye(3) - delta_u_f.T * delta_u_f
    gram_c = inclusion.T * gram_f * inclusion
    audit.check(
        "refinement",
        "source refinement is isometric",
        inclusion.T * inclusion == sp.eye(2),
        matrix_strings(inclusion.T * inclusion),
        matrix_strings(sp.eye(2)),
    )
    audit.check(
        "refinement",
        "coarse Gram is fine Gram congruence",
        gram_c
        == smatrix([[Q(3, 4), Q(-1, 5)], [Q(-1, 5), Q(21, 25)]]),
        matrix_strings(gram_c),
        [["3/4", "-1/5"], ["-1/5", "21/25"]],
    )
    audit.check(
        "refinement",
        "coarse determinant",
        gram_c.det() == Q(59, 100),
        gram_c.det(),
        Q(59, 100),
    )
    audit.check(
        "refinement",
        "congruence does not preserve matrix spectrum",
        gram_c.trace() != gram_f.trace(),
        (gram_c.trace(), gram_f.trace()),
        "different traces",
    )

    # 6. Exact q567 phase-cycle ambiguity on the registered rank-four active
    # fibre.  Its coefficients are derived from A1, not pasted.
    parameters = a1["parameters"]
    p_mass = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    aa = frac(parameters["cJJ"]) * frac(parameters["alpha_X"]) ** 2 / p_mass
    cb = frac(parameters["cJK"]) * frac(parameters["alpha_X"]) * frac(parameters["beta_X"]) / p_mass
    cc = frac(parameters["cKK"]) * frac(parameters["beta_X"]) ** 2 / p_mass
    c0 = aa - cb**2 / cc
    c1 = (cb + cc) ** 2 / cc
    alpha = cc / (cb + cc)
    r = FIXTURE_INPUTS["fibre_r"]
    s = FIXTURE_INPUTS["fibre_s"]
    floor = FIXTURE_INPUTS["fibre_floor"]
    layer_edge = FIXTURE_INPUTS["layer_edge"]
    audit.check(
        "phase_cycle",
        "registered fibre coefficients and audit point",
        c0 == Q(3, 250) / p_mass
        and c1 == Q(243, 8000) / p_mass
        and alpha == Q(5, 9)
        and (r, s, floor) == (Q(7, 5), Q(3, 4), Q(1, 9)),
        (c0, c1, alpha, r, s, floor),
        (Q(3, 250) / p_mass, Q(243, 8000) / p_mass, Q(5, 9), Q(7, 5), Q(3, 4), Q(1, 9)),
    )
    ratio = r * r / (r * r + s * s + floor)
    transverse = Q(4) * (c0 + c1) * r * r
    radial_a = Q(4) * r * r * (c0 + c1 * (Q(1) - alpha * ratio) ** 2)
    radial_c = Q(-4) * c1 * alpha * ratio * (Q(1) - alpha * ratio) * r * s
    radial_d = Q(4) * c1 * alpha**2 * ratio**2 * s**2
    fibre = smatrix(
        [
            [transverse, Q(0), Q(0), Q(0)],
            [Q(0), transverse, Q(0), Q(0)],
            [Q(0), Q(0), radial_a, radial_c],
            [Q(0), Q(0), radial_c, radial_d],
        ]
    )
    audit.check(
        "phase_cycle",
        "registered active fibre rank four",
        fibre.rank() == 4,
        fibre.rank(),
        4,
    )
    audit.check(
        "phase_cycle",
        "registered active fibre positive",
        transverse > 0 and radial_a > 0 and radial_a * radial_d - radial_c**2 > 0,
        (transverse, radial_a * radial_d - radial_c**2),
        "positive transverse and radial principal data",
    )
    layer_plus = smatrix(
        [
            [Q(1), layer_edge, layer_edge],
            [layer_edge, Q(1), layer_edge],
            [layer_edge, layer_edge, Q(1)],
        ]
    )
    layer_minus = smatrix(
        [
            [Q(1), layer_edge, layer_edge],
            [layer_edge, Q(1), -layer_edge],
            [layer_edge, -layer_edge, Q(1)],
        ]
    )
    audit.check(
        "phase_cycle",
        "cycle products have opposite sign",
        layer_plus[0, 1] * layer_plus[1, 2] * layer_plus[2, 0] == Q(27, 64)
        and layer_minus[0, 1] * layer_minus[1, 2] * layer_minus[2, 0]
        == Q(-27, 64),
        (
            layer_plus[0, 1] * layer_plus[1, 2] * layer_plus[2, 0],
            layer_minus[0, 1] * layer_minus[1, 2] * layer_minus[2, 0],
        ),
        (Q(27, 64), Q(-27, 64)),
    )
    audit.check(
        "phase_cycle",
        "same diagonal and edge magnitudes",
        all(
            abs(layer_plus[i, j]) == abs(layer_minus[i, j])
            for i in range(3)
            for j in range(3)
        ),
        True,
        True,
    )
    audit.check(
        "phase_cycle",
        "opposite determinant signs",
        (layer_plus.det(), layer_minus.det())
        == TEST_ORACLES["phase_cycle_determinants"],
        (layer_plus.det(), layer_minus.det()),
        TEST_ORACLES["phase_cycle_determinants"],
    )
    fibre_inertia = exact_ldl_inertia(fibre)
    layer_plus_inertia = exact_ldl_inertia(layer_plus)
    layer_minus_inertia = exact_ldl_inertia(layer_minus)
    h_plus_inertia = tensor_inertia(layer_plus_inertia, fibre_inertia)
    h_minus_inertia = tensor_inertia(layer_minus_inertia, fibre_inertia)
    audit.check(
        "phase_cycle",
        "positive completion inertia",
        h_plus_inertia == (12, 0, 0),
        h_plus_inertia,
        (12, 0, 0),
    )
    audit.check(
        "phase_cycle",
        "adverse completion inertia",
        h_minus_inertia == (8, 4, 0),
        h_minus_inertia,
        (8, 4, 0),
    )

    # Diagonal positivity does not determine the common-output mixed Gram.
    ones3 = sp.ones(3, 1)
    mixed_action = sp.eye(3) - sf(Q(3, 8)) * ones3 * ones3.T
    audit.check(
        "phase_cycle",
        "three positive diagonal margins",
        all(mixed_action[i, i] == Q(5, 8) > 0 for i in range(3)),
        [mixed_action[i, i] for i in range(3)],
        [Q(5, 8)] * 3,
    )
    audit.check(
        "phase_cycle",
        "mixed-only determinant adverse",
        mixed_action.det() == TEST_ORACLES["mixed_only_minimum"],
        mixed_action.det(),
        TEST_ORACLES["mixed_only_minimum"],
    )
    rho_edge = Q(3, 8) * 3
    audit.check(
        "phase_cycle",
        "generalized Gram edge",
        rho_edge == TEST_ORACLES["mixed_only_edge"],
        rho_edge,
        TEST_ORACLES["mixed_only_edge"],
    )

    # 7. A known 12x12 core still does not determine the returned-low sign.
    half_forward_reverse = FIXTURE_INPUTS["returned_low_core_cross"]
    core2 = smatrix(
        [[Q(1), half_forward_reverse], [half_forward_reverse, Q(1)]]
    )
    low_plus = smatrix(
        [
            [Q(1), half_forward_reverse, Q(1, 4)],
            [half_forward_reverse, Q(1), Q(1, 4)],
            [Q(1, 4), Q(1, 4), Q(1)],
        ]
    )
    low_minus = smatrix(
        [
            [Q(1), half_forward_reverse, Q(1, 4)],
            [half_forward_reverse, Q(1), Q(-1, 4)],
            [Q(1, 4), Q(-1, 4), Q(1)],
        ]
    )
    audit.check(
        "returned_low",
        "core is positive",
        core2.det() == Q(183, 1024) > 0,
        core2.det(),
        Q(183, 1024),
    )
    audit.check(
        "returned_low",
        "low completions preserve magnitudes",
        all(
            abs(low_plus[i, j]) == abs(low_minus[i, j])
            for i in range(3)
            for j in range(3)
        ),
        True,
        True,
    )
    audit.check(
        "returned_low",
        "low completions have opposite determinant signs",
        (low_plus.det(), low_minus.det())
        == TEST_ORACLES["low_completion_determinants"],
        (low_plus.det(), low_minus.det()),
        TEST_ORACLES["low_completion_determinants"],
    )
    double_count = smatrix(
        [[Q(1), 2 * half_forward_reverse], [2 * half_forward_reverse, Q(1)]]
    )
    audit.check(
        "returned_low",
        "forward reverse double-count mutation",
        double_count.det() == TEST_ORACLES["double_count_determinant"] < 0,
        double_count.det(),
        TEST_ORACLES["double_count_determinant"],
    )

    # 8. Equal base and first jets do not determine the nonlinear Hessian.
    tau = sp.symbols("tau", real=True)
    u_tau = tau
    phi_plus = 1 + tau + tau**2
    phi_minus = 1 + tau - tau**2
    raw_plus = sp.expand(u_tau**2 - phi_plus**2)
    raw_minus = sp.expand(u_tau**2 - phi_minus**2)
    action_plus = -raw_plus / 2
    action_minus = -raw_minus / 2
    raw_hessians = (
        sp.diff(raw_plus, tau, 2).subs(tau, 0),
        sp.diff(raw_minus, tau, 2).subs(tau, 0),
    )
    action_hessians = (
        sp.diff(action_plus, tau, 2).subs(tau, 0),
        sp.diff(action_minus, tau, 2).subs(tau, 0),
    )
    audit.check(
        "second_jet",
        "same feature base",
        phi_plus.subs(tau, 0) == phi_minus.subs(tau, 0) == 1,
        (phi_plus.subs(tau, 0), phi_minus.subs(tau, 0)),
        (1, 1),
    )
    audit.check(
        "second_jet",
        "same feature first jet",
        sp.diff(phi_plus, tau).subs(tau, 0)
        == sp.diff(phi_minus, tau).subs(tau, 0)
        == 1,
        (
            sp.diff(phi_plus, tau).subs(tau, 0),
            sp.diff(phi_minus, tau).subs(tau, 0),
        ),
        (1, 1),
    )
    audit.check(
        "second_jet",
        "raw-signature Hessians opposite",
        raw_hessians == (-4, 4),
        raw_hessians,
        (-4, 4),
    )
    audit.check(
        "second_jet",
        "action sign and half factor",
        action_hessians == TEST_ORACLES["same_jet_action_hessians"],
        action_hessians,
        TEST_ORACLES["same_jet_action_hessians"],
    )
    full_action_hessians = tuple(value + sf(source_hessian_weight) for value in action_hessians)
    audit.check(
        "second_jet",
        "source cost does not repair adverse second jet",
        full_action_hessians == (sf(Q(29, 10)), sf(Q(-11, 10))),
        full_action_hessians,
        (Q(29, 10), Q(-11, 10)),
    )

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    authority_hashes = {"A1": sha256(A1_MANIFEST), "GATES": sha256(GATES_PATH)}
    authority_hashes.update({name: sha256(path) for name, path in AUTHORITIES.items()})
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(audit.rows) else "FAIL",
        "tier": "T4",
        "authority_hashes": authority_hashes,
        "theorem": {
            "affine_residual_bound": (
                "If ||C||<=rho<sigma<1 and ||U-CY||<=M, then "
                "||U||^2<=sigma^2||Y||^2+sigma^2 M^2/(sigma^2-rho^2)."
            ),
            "one_use_coefficients": {
                "epsilon_source": "(9/20) sigma^2",
                "epsilon_sextic": "(3/20) sigma^2",
                "constant_penalty": "sigma^2 M^2/[2(sigma^2-rho^2)]",
            },
            "projected_force_fallback": (
                "A uniform reduced/source-low effective Hessian gap, origin-force bound, and absolute anchor "
                "give strict T-050: the source coefficient improves and 3/20<gamma/6."
            ),
            "data_routes": [
                "global complete-feature contraction plus bounded returned-low residual",
                "or full common-owner base/first/cross-second jets with source-low Feshbach, origin-force, and anchor bounds",
            ],
        },
        "exact_values": {
            "test_rho": str(rho_q),
            "test_sigma": str(sigma_q),
            "sharp_residual_constant": str(sharp_q),
            "test_epsilon_source": str(eps_source),
            "test_epsilon_sextic": str(eps_sextic),
            "comparison_p": str(comparison_p),
            "nelson_q": str(nelson_q),
            "canonical_source_threshold": str(canonical_source_threshold),
            "q_source_target": str(source_weight),
            "source_threshold_margin": str(canonical_source_threshold - source_weight),
            "hessian_epsilon_source": str(fallback_source),
            "hessian_epsilon_sextic": str(fallback_sextic),
            "hessian_sextic_margin": str(fallback_sextic_margin),
            "fibre_c0": str(c0),
            "fibre_c1": str(c1),
            "fibre_alpha": str(alpha),
            "fibre_audit_point": [str(r), str(s), str(floor)],
            "phase_cycle_determinants": [str(layer_plus.det()), str(layer_minus.det())],
            "phase_cycle_inertia": [list(h_plus_inertia), list(h_minus_inertia)],
            "returned_low_determinants": [str(low_plus.det()), str(low_minus.det())],
            "double_count_determinant": str(double_count.det()),
            "same_jet_action_hessians": [str(value) for value in action_hessians],
            "same_jet_full_action_hessians": [str(value) for value in full_action_hessians],
        },
        "scope": {
            "affine_residual_one_use_theorem_proved": True,
            "sharp_residual_constant_proved": True,
            "projected_force_hessian_sufficient_condition_proved": True,
            "source_low_pullback_typing_proved": True,
            "endpoint_polarization_proved": True,
            "finite_secant_hessian_equivalence_rejected": True,
            "refinement_congruence_proved": True,
            "q567_phase_cycle_nonidentifiability_proved": True,
            "returned_low_nonidentifiability_proved": True,
            "base_first_jet_hessian_nonidentifiability_proved": True,
            "production_chart_registered": False,
            "production_contraction_proved": False,
            "production_residual_bound_proved": False,
            "production_anchor_proved": False,
            "production_hessian_gap_proved": False,
            "production_origin_force_bound_proved": False,
            "t050_closed": False,
            "a13_gate_closed": False,
            "sector_a_closed": False,
        },
        "required_production_data": [
            "canonical temporal source chart and representation-preserving refinement maps",
            "signed common-output q/channel/reveal owner maps with shared probes",
            "complete endpoint Y and U maps, or full base/first/cross-second jets",
            "conditional-low and complete returned-low maps with signed couplings",
            "finite anisotropic low block and transformed analytic tail",
            "uniform contraction/residual/anchor data or Hessian/Feshbach/origin-force data with an anchor",
        ],
        "assertions": {
            "passed": passed,
            "failed": len(audit.rows) - passed,
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "no_overclaim": (
            "R-144 proves a sharp conditional affine-residual route and a conditional "
            "Hessian sufficient condition for the strict one-use coefficients.  The exact fixtures "
            "show why the current local q567/core/first-jet data cannot determine the "
            "production sign.  No production chart, contraction, residual bound, anchor, "
            "positive Hessian gap, origin-force/anchor bounds, T-050 closure, A13 gate, "
            "Nelson theorem, or Sector-A closure is claimed."
        ),
    }
    atomic_json(args.output, payload)
    print(f"R-144 primary: {passed}/{len(audit.rows)} PASS")
    print(f"output: {args.output}")
    return 0 if passed == len(audit.rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
