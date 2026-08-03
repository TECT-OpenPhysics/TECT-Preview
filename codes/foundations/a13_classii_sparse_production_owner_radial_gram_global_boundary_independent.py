#!/usr/bin/env python3
"""Independent standard-library Fraction audit for the A13 R-166 result."""

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
RESULT_ID = "A13-CLASSII-SPARSE-PRODUCTION-OWNER-RADIAL-GRAM-GLOBAL-BOUNDARY"
LEDGER_ID = "R-166"
SLUG = "sparse-production-owner-radial-gram-global-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-independent-{SLUG}" / "result.json"

A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_MANIFEST = CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R153_MANIFEST = CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json"
R164_MANIFEST = CLAIM_DIR / "classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction_manifest.json"
R165_MANIFEST = CLAIM_DIR / "classii_sparse_production_owner_harmonic_coercivity_compact_annulus_boundary_manifest.json"

SCOPE = {
    "fixed_side_16_torus": True,
    "fixed_finite_sparse_p_2p_4p_chart": True,
    "unit_regulator_multipliers_p_2p_4p": True,
    "only_declared_past_and_fresh_modes": True,
    "positive_a7_floor": True,
    "strict_past_conditioned": True,
    "whitened_antipodal_source_coordinates": True,
    "exact_continuum_torus_average": True,
    "fresh_4p_final_root": True,
    "all_past_amplitudes": True,
    "r165_open_annulus_closed": True,
    "complete_multi_root_owner": False,
    "random_nonlinear_revisit_controls": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-166 proves K_owner >= -9I/10 for every whitened past amplitude on only the "
    "fixed side-16 exact nonaliased R-153 p:2p strict-past and fresh-4p twelve-dimensional "
    "conditional fibre with unit retained regulator multipliers and positive floor. It closes "
    "the R-165 annulus on that fibre. It does not prove the complete multi-root production "
    "owner, other harmonics or cross blocks, random/nonlinear/revisit feedback, shifted low "
    "variables, removal, T-050, A13, Nelson or an interacting measure, any physical phase, "
    "morphology or PDE, or Sector A."
)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": encode(actual), "expected": encode(expected)})

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def encode(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=str)


def fraction(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path: Path, payload: dict[str, object]) -> None:
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


def dot(left: list[F], right: list[F]) -> F:
    return sum((a * b for a, b in zip(left, right, strict=True)), F())


def matvec(matrix: list[list[F]], vector: list[F]) -> list[F]:
    return [dot(row, vector) for row in matrix]


def outer(left: list[F], right: list[F]) -> list[list[F]]:
    return [[a * b for b in right] for a in left]


def matrix_add(*matrices: list[list[F]]) -> list[list[F]]:
    return [[sum((matrix[i][j] for matrix in matrices), F()) for j in range(6)] for i in range(6)]


def matrix_sub(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [[left[i][j] - right[i][j] for j in range(6)] for i in range(6)]


def scale(vector: list[F], factor: F) -> list[F]:
    return [factor * item for item in vector]


def pauli_generators() -> tuple[list[list[F]], ...]:
    zero = lambda: [[F() for _ in range(6)] for _ in range(6)]
    s1, s2, s3 = zero(), zero(), zero()
    for i, j in ((0, 1), (1, 0), (3, 4), (4, 3)):
        s1[i][j] = F(1)
    for i, j, value in ((0, 4, 1), (4, 0, 1), (1, 3, -1), (3, 1, -1)):
        s2[i][j] = F(value)
    for i, value in ((0, 1), (1, -1), (3, 1), (4, -1)):
        s3[i][i] = F(value)
    return s1, s2, s3


def gram_decomposition(w: list[F], floor: F) -> tuple[list[list[F]], list[list[F]], list[list[F]]]:
    generators = pauli_generators()
    alpha = F(5, 9)
    rho = dot(w, w)
    d = rho + floor
    projector_w = [w[0], w[1], F(), w[3], w[4], F()]
    lam = dot(projector_w, projector_w) / d
    bj = [[F() for _ in range(6)] for _ in range(6)]
    bl = [[F() for _ in range(6)] for _ in range(6)]
    for generator in generators:
        sw = matvec(generator, w)
        moment = dot(w, sw)
        p = scale(sw, F(2))
        ell = scale([sw[i] - alpha * moment * w[i] / d for i in range(6)], F(2))
        bj = matrix_add(bj, outer(p, p))
        bl = matrix_add(bl, outer(ell, ell))
    plain = scale(projector_w, F(2))
    radial = scale([projector_w[i] - alpha * lam * w[i] for i in range(6)], F(2))
    correction = matrix_sub(outer(radial, radial), outer(plain, plain))
    return bj, bl, correction


def polynomial(g: int, constants: dict[str, F]) -> F:
    value = F(g)
    return constants["A"] * value**4 - constants["B2"] * value**2 - constants["B1"] * value - constants["D0"]


def derivative(g: int, constants: dict[str, F]) -> F:
    value = F(g)
    return 4 * constants["A"] * value**3 - 2 * constants["B2"] * value - constants["B1"]


def second(g: int, constants: dict[str, F]) -> F:
    value = F(g)
    return 12 * constants["A"] * value**2 - 2 * constants["B2"]


def laurent_multiply(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    result: dict[int, F] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode + right_mode
            result[mode] = result.get(mode, F()) + left_value * right_value
    return {mode: value for mode, value in result.items() if value != 0}


def laurent_derivative(polynomial: dict[int, F]) -> dict[int, F]:
    return {mode: F(mode) * value for mode, value in polynomial.items() if mode != 0}


def laurent_scale(polynomial: dict[int, F], factor: F) -> dict[int, F]:
    return {mode: factor * value for mode, value in polynomial.items()}


def quotient_directional_jet(
    wx: F, wy: F, floor: F, zx: F, zy: F
) -> dict[str, F]:
    numerator = (wx * wx, 2 * wx * zx, zx * zx)
    denominator = (
        wx * wx + wy * wy + floor,
        2 * (wx * zx + wy * zy),
        zx * zx + zy * zy,
    )
    q0 = numerator[0] / denominator[0]
    q1 = (numerator[1] - denominator[1] * q0) / denominator[0]
    q2 = (
        numerator[2] - denominator[1] * q1 - denominator[2] * q0
    ) / denominator[0]
    wz = wx * zx + wy * zy
    tangent_norm = zx * zx + zy * zy
    inner = wx * zx - q0 * wz
    first_formula = 2 * inner / denominator[0]
    second_formula = (
        2 * (zx * zx - q0 * tangent_norm) / denominator[0]
        - 8 * inner * wz / denominator[0] ** 2
    )
    second_mutant = (
        2 * (zx * zx - q0 * tangent_norm) / denominator[0]
        - 4 * inner * wz / denominator[0] ** 2
    )
    gradient = (
        2 * (wx - q0 * wx) / denominator[0],
        -2 * q0 * wy / denominator[0],
    )
    radius_square = wx * wx + wy * wy
    return {
        "series_first": q1,
        "series_second": 2 * q2,
        "formula_first": first_formula,
        "formula_second": second_formula,
        "mutant_second": second_mutant,
        "gradient_square_paid": radius_square * (gradient[0] ** 2 + gradient[1] ** 2),
        "hessian_paid": radius_square * abs(second_formula),
        "tangent_norm": tangent_norm,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = load(A1_MANIFEST)
    r130, r153, r164, r165 = (load(path) for path in (R130_MANIFEST, R153_MANIFEST, R164_MANIFEST, R165_MANIFEST))
    r165_result_path = REPO / r165["files"]["primary_result"]["path"]
    r165_result = load(r165_result_path)
    audit.check(
        "authority",
        "dependency identities",
        [r130["result_ledger_id"], r153["result_ledger_id"], r164["result_ledger_id"], r165["result_ledger_id"]]
        == ["R-130", "R-153", "R-164", "R-165"]
        and sha256(r165_result_path) == r165["files"]["primary_result"]["sha256"],
        [r130["result_ledger_id"], r153["result_ledger_id"], r164["result_ledger_id"], r165["result_ledger_id"], sha256(r165_result_path)],
        ["R-130", "R-153", "R-164", "R-165", r165["files"]["primary_result"]["sha256"]],
    )
    parameters = a1["parameters"]
    p_mass = fraction(parameters["M_X"]) ** 2 + fraction(parameters["classii_mass_regularizer"])
    raw_a = fraction(parameters["cJJ"]) * fraction(parameters["alpha_X"]) ** 2 / p_mass
    raw_b = fraction(parameters["cJK"]) * fraction(parameters["alpha_X"]) * fraction(parameters["beta_X"]) / p_mass
    raw_c = fraction(parameters["cKK"]) * fraction(parameters["beta_X"]) ** 2 / p_mass
    c0, c1, alpha = F(3, 250) / p_mass, F(243, 8000) / p_mass, F(5, 9)
    audit.check("coefficients", "c0 independently completed", raw_a - raw_b**2 / raw_c == c0, raw_a - raw_b**2 / raw_c, c0)
    audit.check("coefficients", "c1 independently completed", (raw_b + raw_c) ** 2 / raw_c == c1, (raw_b + raw_c) ** 2 / raw_c, c1)
    audit.check("coefficients", "alpha independently completed", raw_c / (raw_b + raw_c) == alpha, raw_c / (raw_b + raw_c), alpha)
    audit.check("coefficients", "outward coefficient bounds", c0 < F(3, 1000) and c1 < F(243, 32000), [c0, c1], ["<3/1000", "<243/32000"])

    fixtures = (
        [F(1), F(2), F(3), F(4), F(5), F(6)],
        [F(-2), F(1, 3), F(5, 2), F(-7, 4), F(3), F(1, 5)],
        [F(), F(), F(7), F(), F(), F(-3)],
        [F(4), F(-5), F(), F(2), F(1), F()],
    )
    residuals: list[F] = []
    for fixture in fixtures:
        bj, bl, correction = gram_decomposition(fixture, F(1, 10**12))
        residuals.extend(item for row in matrix_sub(matrix_sub(bl, bj), correction) for item in row)
    audit.check("gram", "independent rational Fierz fixtures", all(item == 0 for item in residuals), residuals, "all zero")
    pure_singlet_correction = gram_decomposition(fixtures[2], F(1, 10**12))[2]
    audit.check("gram", "pure singlet correction", all(item == 0 for row in pure_singlet_correction for item in row), "checked", "zero")

    # Independently recover both quotient derivatives from exact Taylor-series
    # division, then test the global payments on boundary-sensitive fixtures.
    quotient_fixtures = (
        (F(1), F(2), F(1, 10), F(3), F(-1)),
        (F(0), F(2), F(1, 10**12), F(1), F(3)),
        (F(3), F(0), F(1, 7), F(-2), F(5)),
        (F(1, 1000), F(7, 5), F(1, 10**12), F(11, 3), F(-4, 7)),
    )
    quotient_jets = [quotient_directional_jet(*fixture) for fixture in quotient_fixtures]
    audit.check(
        "radial",
        "exact quotient directional series",
        all(jet["series_first"] == jet["formula_first"] for jet in quotient_jets),
        [[jet["series_first"], jet["formula_first"]] for jet in quotient_jets],
        "all equal",
    )
    audit.check(
        "radial",
        "quotient gradient boundary fixtures",
        all(jet["gradient_square_paid"] <= 1 for jet in quotient_jets),
        [jet["gradient_square_paid"] for jet in quotient_jets],
        "all <=1",
    )
    audit.check(
        "radial",
        "exact quotient Hessian and factor-four mutant",
        all(jet["series_second"] == jet["formula_second"] for jet in quotient_jets)
        and any(jet["series_second"] != jet["mutant_second"] for jet in quotient_jets),
        [[jet["series_second"], jet["formula_second"], jet["mutant_second"]] for jet in quotient_jets],
        "formula equal; mutant rejected",
    )
    audit.check(
        "radial",
        "quotient Hessian boundary fixtures",
        all(jet["hessian_paid"] <= 6 * jet["tangent_norm"] for jet in quotient_jets),
        [[jet["hessian_paid"], 6 * jet["tangent_norm"]] for jet in quotient_jets],
        "all paid",
    )
    grad_bound, hessian_bound = F(1), F(6)
    da = 2 * (1 + alpha * (1 + grad_bound))
    d2a = 2 * alpha * (hessian_bound + 2 * grad_bound)
    c_zero = F(8)
    c_first = 2 * (2 * da + 4)
    c_half = da**2 + 2 * d2a + 4
    audit.check("radial", "Da and D2a bounds", [da, d2a] == [F(38, 9), F(80, 9)], [da, d2a], [F(38, 9), F(80, 9)])
    audit.check("radial", "C value envelope", c_zero == 8, c_zero, 8)
    audit.check("radial", "C first envelope", c_first == F(224, 9), c_first, F(224, 9))
    audit.check("radial", "C half-Hessian envelope", c_half == F(3208, 81), c_half, F(3208, 81))
    past = {-2: F(2), -1: F(3), 1: F(3), 2: F(2)}
    expected_current = laurent_scale(
        laurent_multiply(past, laurent_derivative(past)), F(2)
    )
    fresh4 = {-4: F(1), 4: F(1)}
    fresh4_second = laurent_scale(
        laurent_multiply(fresh4, laurent_derivative(fresh4)), F(4)
    )
    valid_resonance = laurent_multiply(expected_current, fresh4_second).get(0, F())
    fresh2 = {-2: F(1), 2: F(1)}
    wrong_root_second = laurent_scale(
        laurent_multiply(fresh2, laurent_derivative(fresh2)), F(4)
    )
    wrong_root_resonance = laurent_multiply(expected_current, wrong_root_second).get(0, F())
    audit.check(
        "harmonic",
        "exact current nonresonance and wrong-root mutant",
        valid_resonance == 0
        and set(expected_current).issubset(set(range(-4, 5)))
        and set(fresh4_second) == {-8, 8}
        and wrong_root_resonance != 0,
        [valid_resonance, sorted(expected_current), sorted(fresh4_second), wrong_root_resonance],
        [0, "modes within [-4,4]", [-8, 8], "nonzero"],
    )

    half = F(1, 2)
    cosine2 = {-2: half, 2: half}
    cosine2_square = laurent_multiply(cosine2, cosine2)
    cosine2_fourth = laurent_multiply(cosine2_square, cosine2_square)
    sine4_square = {-8: F(-1, 4), 0: half, 8: F(-1, 4)}
    fixture_product = laurent_multiply(cosine2_fourth, sine4_square).get(0, F())
    fixture_f = cosine2_fourth.get(0, F())
    fixture_q = sine4_square[0]
    source_square = cosine2_square[0] ** 2 * fixture_q
    audit.check(
        "harmonic",
        "exact source-coordinate coercivity and decorrelation mutant",
        fixture_product == F(5, 32)
        and source_square == F(1, 8)
        and fixture_product >= source_square
        and fixture_product < fixture_f * fixture_q,
        [fixture_product, source_square, fixture_f * fixture_q],
        [F(5, 32), F(1, 8), "false larger RHS"],
    )

    predecessor = r165_result["diagnostics"]
    covariance = predecessor["covariance_bounds"]
    volume = fraction(a1["parameters"]["Lx"]) * fraction(a1["parameters"]["Ly"]) * fraction(a1["parameters"]["Lz"])
    cp_min, cp_max = fraction(covariance["cp_min"]), fraction(covariance["cp_max"])
    c4_min, c4_max = fraction(covariance["c4_min"]), fraction(covariance["c4_max"])
    trace4_max = fraction(covariance["trace4_max"])
    gamma_past = fraction(predecessor["past_derivative_covariance_upper"])
    p2 = gamma_past * volume / (10 * cp_max)
    sqrt_factor = F(301, 100)
    c0_upper, c1_upper = F(3, 1000), F(243, 32000)
    l_corr = c1_upper * c_first
    h_corr = c1_upper * c_half
    h_trace = 12 * (c0_upper + c1_upper) + h_corr
    audit.check(
        "ledger",
        "paid radial constants",
        volume == fraction(predecessor["volume"])
        and p2 == F(5, 32)
        and 2 * cp_max * trace4_max < sqrt_factor**2
        and [l_corr, h_corr, h_trace] == [F(189, 1000), F(1203, 4000), F(3423, 8000)],
        [volume, p2, 2 * cp_max * trace4_max, l_corr, h_corr, h_trace],
        [fraction(predecessor["volume"]), F(5, 32), f"<({sqrt_factor})^2", F(189, 1000), F(1203, 4000), F(3423, 8000)],
    )

    prefactor = p2 * cp_max * c4_max / volume
    constants = {
        "A": F(9, 10) * c4_min * cp_min**2 / volume**2,
        "B2": prefactor * (32 * c_zero * c1_upper + 32 * l_corr + 8 * h_corr),
        "B1": 32 * l_corr * p2 * c4_max * sqrt_factor / volume,
        "D_fresh": c_zero * c1_upper * 32 * p2 * c4_max * trace4_max / volume,
        "D_trace": h_trace * c4_max * gamma_past,
    }
    constants["D0"] = constants["D_fresh"] + constants["D_trace"]
    expected = {
        "A": F(625, 21040201728),
        "B2": F(25995, 87359488),
        "B1": F(1323, 8192000),
        "D_fresh": F(729, 30294016),
        "D_trace": F(85575, 698875904),
        "D0": F(4402893, 30051663872),
    }
    audit.check("ledger", "independent exact constants", constants == expected, constants, expected)
    audit.check("ledger", "C value B2 debit", 32 * c_zero * c1_upper * prefactor == F(1215, 21839872), 32 * c_zero * c1_upper * prefactor, F(1215, 21839872))
    audit.check("ledger", "derivative B2 debit", prefactor * (32 * l_corr + 8 * h_corr) == F(21135, 87359488), prefactor * (32 * l_corr + 8 * h_corr), F(21135, 87359488))
    audit.check("ledger", "fresh value debit", constants["D_fresh"] == F(729, 30294016), constants["D_fresh"], F(729, 30294016))
    audit.check("ledger", "trace debit", constants["D_trace"] == F(85575, 698875904), constants["D_trace"], F(85575, 698875904))

    d70, d71 = derivative(70, constants), derivative(71, constants)
    dd40, dd41, dd70 = second(40, constants), second(41, constants), second(70, constants)
    lower = polynomial(70, constants) + d70
    margin = lower + F(9, 10)
    audit.check("minimum", "curvature switch bracket", dd40 < 0 < dd41, [dd40, dd41], "negative,positive")
    audit.check("minimum", "unique derivative root bracket", d70 == -F(1360786403, 1277632512000) < 0 and d71 == F(97738714417, 876455903232000) > 0, [d70, d71], "negative,positive")
    audit.check("minimum", "convexity at bracket", dd70 == F(6865745, 5962285056) > 0, dd70, ">0")
    audit.check("minimum", "global lower certificate", lower == -F(332863942666997, 439505584128000), lower, -F(332863942666997, 439505584128000))
    audit.check("minimum", "strict target margin", margin == F(62691083048203, 439505584128000) > 0, margin, ">0")
    rho = F(1, 110)
    audit.check("threshold", "R-164 target", F(10, 11) - rho == F(9, 10), F(10, 11) - rho, F(9, 10))
    audit.check("threshold", "strict reduced gap", margin > 0 and rho > 0, [margin, rho], "positive")
    audit.check("scope", "open-gate firewall", SCOPE["all_past_amplitudes"] and SCOPE["r165_open_annulus_closed"] and not SCOPE["complete_multi_root_owner"] and not SCOPE["t050_closed"] and not SCOPE["sector_a_closed"] and "does not prove" in NO_OVERCLAIM, SCOPE, "one sparse fibre only")

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "status": "PASS",
        "diagnostics": {
            "coefficients": {"c0": c0, "c1": c1, "alpha": alpha},
            "correction_envelopes": {"C0": c_zero, "LC": c_first, "HC": c_half, "paid_LC": l_corr, "paid_HC": h_corr, "trace_H": h_trace},
            "quotient_bounds": {"w_grad_lambda": grad_bound, "w2_hessian_lambda": hessian_bound},
            "harmonic_source_coordinate_constant": 1,
            "polynomial_constants": constants,
            "derivative_at_70": d70,
            "derivative_at_71": d71,
            "second_at_40": dd40,
            "second_at_41": dd41,
            "second_at_70": dd70,
            "minimum_bracket": "70<G_*<71",
            "global_lower_bound": lower,
            "owner_margin_above_minus_9_10": margin,
            "owner_floor": -F(9, 10),
            "rho": rho,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {"A1": sha256(A1_MANIFEST), "R-130": sha256(R130_MANIFEST), "R-153": sha256(R153_MANIFEST), "R-164": sha256(R164_MANIFEST), "R-165": sha256(R165_MANIFEST), "R-165-result": sha256(r165_result_path)},
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
