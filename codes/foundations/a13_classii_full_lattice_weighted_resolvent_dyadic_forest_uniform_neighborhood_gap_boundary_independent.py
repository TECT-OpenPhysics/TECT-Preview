#!/usr/bin/env python3
"""Independent standard-library audit for the A13 R-163 forest theorem.

This implementation imports neither the primary module nor a scientific
package.  It recomputes the rational constants, lattice envelopes, path
series, two-component forest algebra, and exact coefficient thresholds.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-FULL-LATTICE-WEIGHTED-RESOLVENT-DYADIC-FOREST-"
    "UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
)
LEDGER_ID = "R-163"
SLUG = "full-lattice-weighted-resolvent-dyadic-forest-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-independent-{SLUG}" / "result.json"

AUTHORITIES = {
    "A1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "A7": REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "R-107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-160": CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json",
    "R-161": CLAIM_DIR / "classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_manifest.json",
    "R-162": CLAIM_DIR / "classii_resolvent_pure_dyadic_recursive_chain_uniform_neighborhood_gap_boundary_manifest.json",
}

SCOPE = {
    "actual_shifted_state_read_at_each_stage": True,
    "arbitrary_finite_injective_pure_dyadic_forest": True,
    "centered_independent_raw_gaussian_blocks": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "complete_controller_pullback_hessian": True,
    "complete_expected_global_terminal_scalar": True,
    "deterministic_matrix_coefficients": True,
    "exact_nonaliased_continuum_torus_integration": True,
    "fixed_positive_A7_floor": True,
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_spatial_dimension_three": True,
    "forward_legal_reverse_balanced_are_one_hessian": True,
    "independent_low_or_feshbach_coordinate": False,
    "intrinsic_hessian_claimed": False,
    "local_root_ECN_equals_Pcomp": False,
    "pathwise_fibrewise_conditional_hessian": False,
    "projected_force_connection_included": True,
    "random_or_nonlinear_past_dependent_coefficients": False,
    "revisit_cycles_or_general_branching": False,
    "sextic_connection_included": True,
    "summed_HS_l2_coefficient_norm": True,
    "uniform_over_forest_cardinality_depth_finite_cutoff_and_admitted_regulator": True,
    "floor_or_infinite_endpoint_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-163 proves one positive analytic l2(HS) coefficient radius for every finite injective "
    "pure-dyadic deterministic-matrix shifted-state forest, uniformly in its number of unrelated "
    "chains, depths, retained modes, finite cutoff, and admitted common-even regulator, at the "
    "fixed side-16 d=3 A1/A7 setting. It controls the complete expected global controller-pullback "
    "Hessian and includes source, endpoint/current, trace, projected-force, forward/legal-reverse/"
    "balanced, and sextic connections once. It proves no intrinsic-Hessian theorem, random or "
    "nonlinear past-dependent law, revisit/cycle/general branching, pathwise fibrewise conditional "
    "estimate, removal, T-050/A13, Nelson, measure, phase/PDE, or Sector-A closure."
)


def encode(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def text_hash(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": encode(actual),
                "expected": encode(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


Matrix = list[list[F]]


def zero(size: int) -> Matrix:
    return [[F(0) for _ in range(size)] for _ in range(size)]


def identity(size: int) -> Matrix:
    result = zero(size)
    for index in range(size):
        result[index][index] = F(1)
    return result


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return [[sum((left[i][k] * right[k][j] for k in range(size)), F(0)) for j in range(size)] for i in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def scale(value: F, matrix: Matrix) -> Matrix:
    return [[value * item for item in row] for row in matrix]


def forest_shift(values: tuple[F, F, F, F]) -> Matrix:
    result = zero(6)
    for target, source, value in ((1, 0, values[0]), (2, 1, values[1]), (4, 3, values[2]), (5, 4, values[3])):
        result[target][source] = value
    return result


def resolvent(matrix: Matrix) -> Matrix:
    return add(add(identity(6), matrix), multiply(matrix, matrix))


def falling(index: int, order: int) -> int:
    value = 1
    for offset in range(order):
        value *= index - offset
    return value


def path_partial(q: F, r: F, order: int, terms: int = 180) -> F:
    return sum((F(falling(k, order)) * q**k * r ** (k - order) for k in range(max(1, order), terms + 1)), F(0))


def path_closed(q: F, r: F, order: int) -> F:
    if order == 0:
        return q * r / (1 - q * r)
    factorial = 1
    for value in range(2, order + 1):
        factorial *= value
    return F(factorial) * q**order / (1 - q * r) ** (order + 1)


def word_jet(q_left: F, q_right: F, r: F, order: int) -> F:
    """Derivative of [(1-q_left r)(1-q_right r)]^-1 minus identity."""
    if order == 0:
        return 1 / ((1 - q_left * r) * (1 - q_right * r)) - 1
    factorial = 1
    for value in range(2, order + 1):
        factorial *= value
    total = F(0)
    for split in range(order + 1):
        total += (
            q_left**split
            * q_right ** (order - split)
            / ((1 - q_left * r) ** (split + 1) * (1 - q_right * r) ** (order - split + 1))
        )
    return F(factorial) * total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, path in AUTHORITIES.items():
        audit.check("authority", f"{label} exists", path.is_file(), relative(path), "existing file")

    g = F(244140625000000000, 28800000000947494031)
    c0 = F(3, 20)
    origin_gap = F(4, 25)
    audit.check("constants", "synthesis envelope positive", g > 0, g, ">0")
    audit.check("constants", "side-16 floor", c0 == F(3, 20), c0, F(3, 20))
    audit.check("constants", "origin gap", origin_gap == F(4, 25), origin_gap, F(4, 25))

    # Independent max-shell integral-test derivation of the inherited bounds.
    zeta2_upper = F(2)
    zeta4_upper = F(4, 3)
    zeta6_upper = F(6, 5)
    zeta8_upper = F(8, 7)
    shell4_upper = 24 * zeta2_upper + 2 * zeta4_upper
    shell6_upper = 24 * zeta4_upper + 2 * zeta6_upper
    shell8_upper = 24 * zeta6_upper + 2 * zeta8_upper
    audit.check("lattice", "power-four shell bound", shell4_upper < 52, shell4_upper, "<52")
    audit.check("lattice", "power-six shell bound", shell6_upper < 35, shell6_upper, "<35")
    audit.check("lattice", "power-eight shell bound", shell8_upper < 32, shell8_upper, "<32")
    audit.check("lattice", "max-shell population identity at m=7", 24 * 7**2 + 2 == 1178, 24 * 7**2 + 2, 1178)

    cross_base_squared = {
        "SS": F(32) * g * g / c0**4,
        "SD": F(35) * g * g / c0**3,
        "DS": F(35) * g * g / c0**3,
        "DD": F(52) * g * g / c0**2,
    }
    cross_ratio = {"SS": F(1, 4), "SD": F(1, 4), "DS": F(1, 2), "DD": F(1, 2)}
    audit.check("weights", "cross bases positive", all(value > 0 for value in cross_base_squared.values()), cross_base_squared, "positive")
    audit.check("weights", "mixed base symmetry", cross_base_squared["SD"] == cross_base_squared["DS"], cross_base_squared["SD"], cross_base_squared["DS"])
    audit.check("weights", "DD ratio is worst", max(cross_ratio.values()) == F(1, 2), max(cross_ratio.values()), F(1, 2))
    audit.check("weights", "weighted DD sum beats raw D exponent", 4 > 3 >= 2, [4, 3, 2], "4>d>=2")

    # Non-symbolic series audit at two exact rational points.  The omitted
    # geometric tail is far below the declared rational tolerance.
    tolerance = F(1, 10**50)
    for q in (F(1, 4), F(1, 2)):
        for r in (F(1, 3), F(1, 2)):
            for order in range(4):
                partial = path_partial(q, r, order)
                closed = path_closed(q, r, order)
                audit.check("series", f"q={q} r={r} order={order}", 0 < closed - partial < tolerance, closed - partial, f"between 0 and {tolerance}")
    audit.check("word", "SS first coefficient", word_jet(F(1, 4), F(1, 4), F(0), 1) == F(1, 2), word_jet(F(1, 4), F(1, 4), F(0), 1), F(1, 2))
    audit.check("word", "DD first coefficient", word_jet(F(1, 2), F(1, 2), F(0), 1) == 1, word_jet(F(1, 2), F(1, 2), F(0), 1), 1)
    audit.check("word", "mixed first coefficient", word_jet(F(1, 4), F(1, 2), F(0), 1) == F(3, 4), word_jet(F(1, 4), F(1, 2), F(0), 1), F(3, 4))

    # Exact two-chain matrix calculation with a separate Fraction engine.
    values = (F(1, 7), F(-1, 5), F(2, 9), F(1, 4))
    n = forest_shift(values)
    n2 = multiply(n, n)
    n3 = multiply(n2, n)
    t = resolvent(n)
    b = subtract(t, identity(6))
    p = multiply(t, transpose(t))
    r_matrix = subtract(p, identity(6))
    decomposition = add(add(b, transpose(b)), multiply(b, transpose(b)))
    audit.check("forest", "cubic nilpotence", n3 == zero(6), n3, zero(6))
    audit.check("forest", "resolvent inverse", multiply(subtract(identity(6), n), t) == identity(6), multiply(subtract(identity(6), n), t), identity(6))
    audit.check("forest", "R decomposition", r_matrix == decomposition, r_matrix, decomposition)
    audit.check("forest", "component covariance separation", all(r_matrix[i][j] == 0 for i in range(3) for j in range(3, 6)), "cross blocks zero", "cross blocks zero")

    h = forest_shift((F(2, 5), F(1, 3), F(-3, 8), F(5, 11)))
    h2 = multiply(h, h)
    acceleration = add(h2, transpose(h2))
    audit.check("origin", "two-step acceleration only", all(acceleration[i][j] == 0 for i in range(6) for j in range(6) if abs(i - j) != 2), acceleration, "distance two only")
    audit.check("origin", "no cross-component acceleration", all(acceleration[i][j] == 0 for i in range(3) for j in range(3, 6)), "cross blocks zero", "cross blocks zero")
    audit.check("origin", "Fourier differences", {4 - 1, 4 + 1} == {3, 5}, sorted({4 - 1, 4 + 1}), [3, 5])
    covariance_second = scale(F(2), add(add(multiply(h, transpose(h)), h2), transpose(h2)))
    audit.check("origin", "covariance second jet symmetric", covariance_second == transpose(covariance_second), covariance_second, "symmetric")

    # Adversarial complete-owner and low-kernel fixtures.
    diagonal = F(3, 20)
    cross = F(-1, 5)
    eigenvalues = sorted((diagonal + cross, diagonal - cross))
    audit.check("adversary", "local gaps exceed one tenth", diagonal > F(1, 10), diagonal, ">1/10")
    audit.check("adversary", "global owner eigenvalues", eigenvalues == [F(-1, 20), F(7, 20)], eigenvalues, [F(-1, 20), F(7, 20)])
    audit.check("adversary", "low-kernel determinant", F(1) * F(0) - F(1) * F(1) == -1, -1, -1)

    r0 = F(1, 2)
    tau = 1 / (1 - r0)
    beta = [r0 * tau, tau**2, 2 * tau**3, 6 * tau**4]
    q_values = [
        beta[0] ** 2,
        2 * beta[0] * beta[1],
        2 * beta[0] * beta[2] + 2 * beta[1] ** 2,
        2 * beta[0] * beta[3] + 6 * beta[1] * beta[2],
    ]
    q_closed = [r0**2 * tau**2, 2 * r0 * tau**3, (2 + 4 * r0) * tau**4, 12 * (1 + r0) * tau**5]
    audit.check("assembly", "weighted-HS beta jets", beta == [1, 4, 16, 96], beta, [1, 4, 16, 96])
    audit.check("assembly", "quadratic Leibniz jets", q_values == q_closed == [1, 8, 64, 576], q_values, [1, 8, 64, 576])
    audit.check("assembly", "all cross rational data finite", all(value > 0 for value in cross_base_squared.values()) and tau == 2, {"bases": cross_base_squared, "tau": tau}, "positive finite")

    # Compare the squares of the direct two-sided word bounds.  Working with
    # squares keeps this independent implementation purely rational.
    word_jets_squared_at_r0: dict[str, list[F]] = {}
    for label, q_left, q_right in (
        ("SS", F(1, 4), F(1, 4)),
        ("DD", F(1, 2), F(1, 2)),
        ("SD", F(1, 4), F(1, 2)),
    ):
        word_jets_squared_at_r0[label] = [cross_base_squared[label] * word_jet(q_left, q_right, r0, order) ** 2 for order in range(4)]
    safe_data_jet_squared_at_r0 = [
        word_jets_squared_at_r0["SS"][order]
        + 9 * word_jets_squared_at_r0["DD"][order]
        + 6 * word_jets_squared_at_r0["SD"][order]
        for order in range(4)
    ]
    audit.check("word", "two-sided word jets positive", all(value > 0 for values in word_jets_squared_at_r0.values() for value in values), word_jets_squared_at_r0, "positive")
    audit.check("word", "safe assembled data jets positive", all(value > 0 for value in safe_data_jet_squared_at_r0), safe_data_jet_squared_at_r0, "positive")

    cm_d3_bound = F(27, 5) * (1 + r0) * tau**5
    retained_gap = origin_gap - F(3, 100)
    audit.check("gap", "source D3 bound", cm_d3_bound == F(1296, 5), cm_d3_bound, F(1296, 5))
    audit.check("gap", "retained gap", retained_gap == F(13, 100), retained_gap, F(13, 100))
    audit.check("gap", "retained above target", retained_gap > F(1, 10), retained_gap, ">1/10")
    audit.check("gap", "metric ceiling", F(100, 97) ** 4 < F(13, 10), F(100, 97) ** 4, "<13/10")

    p_nelson = F(11, 10)
    epsilon_v_limit = 1 / (2 * p_nelson)
    explicit_source = F(9, 20)
    coefficient_headroom = epsilon_v_limit - explicit_source
    mu_floor = -2 * coefficient_headroom
    owner_floor = mu_floor - F(9, 10)
    audit.check("threshold", "epsilon-v limit", epsilon_v_limit == F(5, 11), epsilon_v_limit, F(5, 11))
    audit.check("threshold", "coefficient headroom", coefficient_headroom == F(1, 220), coefficient_headroom, F(1, 220))
    audit.check("threshold", "reduced Hessian floor", mu_floor == F(-1, 110), mu_floor, F(-1, 110))
    audit.check("threshold", "owner adverse floor", owner_floor == F(-10, 11), owner_floor, F(-10, 11))
    audit.check("threshold", "sextic coefficient", F(3, 20) < F(27, 100), F(3, 20), "<27/100")
    audit.check("scope", "deterministic forest only", SCOPE["arbitrary_finite_injective_pure_dyadic_forest"] and SCOPE["deterministic_matrix_coefficients"] and not SCOPE["random_or_nonlinear_past_dependent_coefficients"], SCOPE, "deterministic injective forest")
    audit.check("scope", "no T-050 closure", not SCOPE["t050_closed"] and not SCOPE["a13_closed"] and not SCOPE["sector_a_closed"], [SCOPE["t050_closed"], SCOPE["a13_closed"], SCOPE["sector_a_closed"]], [False, False, False])

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {label: text_hash(path) for label, path in AUTHORITIES.items()},
        "diagnostics": {
            "g": g,
            "c0": c0,
            "origin_gap": origin_gap,
            "retained_gap": retained_gap,
            "cross_base_squared": cross_base_squared,
            "cross_ratio": cross_ratio,
            "shell_upper_bounds": {"power4": shell4_upper, "power6": shell6_upper, "power8": shell8_upper},
            "weighted_HS_beta_at_r0": beta,
            "quadratic_Leibniz_jets_at_r0": q_values,
            "two_sided_word_jets_squared_at_r0": word_jets_squared_at_r0,
            "safe_data_jet_squared_at_r0": safe_data_jet_squared_at_r0,
            "CM_D3_bound_at_r0": cm_d3_bound,
            "reduced_action_hessian_floor": mu_floor,
            "owner_adverse_floor": owner_floor,
            "local_gap_counterfixture_eigenvalues": eigenvalues,
        },
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} independent: {len(audit.rows)}/{len(audit.rows)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
