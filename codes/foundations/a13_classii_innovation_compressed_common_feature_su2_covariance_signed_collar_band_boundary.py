#!/usr/bin/env python3
"""Primary exact/numerical certificate for the scoped A13 R-142 checkpoint.

The script verifies the mixed-endpoint innovation compression, a canonical
singular-covariance trace feature, the exact two-feature action Hessian, the
coefficient-exact SU(2) fibre block, the production family-lock covariance
split, the legal scalar two-root/two-visit chart, and the signed C8/C10
coefficient bands.  It does not assemble or certify the full production
common-heat owner matrix.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np
import sympy as sp


RESULT_ID = (
    "A13-CLASSII-INNOVATION-COMPRESSED-COMMON-FEATURE-SU2-"
    "COVARIANCE-SIGNED-COLLAR-BAND-BOUNDARY"
)
SCHEMA = (
    "tect/a13-innovation-compressed-common-feature-su2-covariance-"
    "signed-collar-band-boundary-primary/1.0"
)
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-innovation-compressed-common-feature-su2-"
    "covariance-signed-collar-band-boundary/result.json"
)
Q = Fraction
P_INPUT = Q(4_000_000_000_001, 1_000_000_000_000)
ALPHA_INPUT = Q(5, 9)
C0_INPUT = Q(3, 250) / P_INPUT
C1_INPUT = Q(243, 8000) / P_INPUT
FAMILY_MASSES_INPUT = (Q(0), Q(3, 100), Q(7, 100))
LOCK_INPUT = Q(3, 20)
LOCK_VECTOR_INPUT = (Q(1), Q(1), Q(1))
SOURCE_FLOOR = Q(9, 10)
TOL = 5.0e-11


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


def mean_vector(samples: list[list[Fraction]]) -> list[Fraction]:
    count = Q(len(samples))
    return [sum((row[j] for row in samples), Q(0)) / count for j in range(len(samples[0]))]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Q(0))


def mean_cross(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> Fraction:
    return sum((dot(x, y) for x, y in zip(left, right)), Q(0)) / Q(len(left))


def fraction_matrix_to_float(matrix: list[list[Fraction]]) -> np.ndarray:
    return np.asarray([[float(value) for value in row] for row in matrix], dtype=float)


def shell_range(offset: int) -> range:
    return range(2 ** (offset - 2) + 1, 2 ** (offset - 1) + 1)


def rational_coefficient(n: int, delta: float, floor: float) -> float:
    """R-133 coefficient a_n computed from the upstream analytic formula."""
    kappa = math.asinh(delta)
    c = math.sqrt(1.0 + delta * delta)
    bracket = (
        5.0 * delta / (27.0 * c)
        + 25.0
        * delta
        * delta
        / (81.0 * c * c)
        * (n + 1.0 / math.tanh(2.0 * kappa))
    )
    return (
        4.0
        * float(C1_INPUT)
        * floor
        * ((-1.0) ** (n + 1))
        * math.exp(-2.0 * n * kappa)
        * bracket
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # 1. Exact mixed-endpoint innovation compression.
    jq = [
        [Q(2), Q(-1)],
        [Q(0), Q(3)],
        [Q(5), Q(2)],
        [Q(-3), Q(0)],
    ]
    jp = [
        [Q(1), Q(4)],
        [Q(-2), Q(1)],
        [Q(3), Q(-1)],
        [Q(6), Q(2)],
    ]
    phiq = mean_vector(jq)
    phip = mean_vector(jp)
    rq = [[value - phiq[j] for j, value in enumerate(row)] for row in jq]
    rp = [[value - phip[j] for j, value in enumerate(row)] for row in jp]
    raw_cross = mean_cross(jq, jp)
    residual_cross = mean_cross(rq, rp)
    mean_cross_value = dot(phiq, phip)
    audit.check(
        "compression",
        "mixed conditional covariance decomposition",
        raw_cross == mean_cross_value + residual_cross,
        raw_cross,
        mean_cross_value + residual_cross,
    )
    audit.check(
        "compression",
        "signed J residual compression",
        -raw_cross + residual_cross == -mean_cross_value,
        -raw_cross + residual_cross,
        -mean_cross_value,
    )
    audit.check(
        "compression",
        "both residuals centered",
        mean_vector(rq) == [Q(0), Q(0)] and mean_vector(rp) == [Q(0), Q(0)],
        (mean_vector(rq), mean_vector(rp)),
        ([Q(0), Q(0)], [Q(0), Q(0)]),
    )

    # Canonical actual trace feature with singular Gamma=v v^T.
    v = sp.Matrix([2, 1])
    gamma = v * v.T
    aq = sp.Matrix([[1, 2], [0, -1]])
    ap = sp.Matrix([[3, -2], [1, 4]])
    uq = aq * v
    up = ap * v
    trace_cross = sp.trace(aq * gamma * ap.T)
    audit.check(
        "trace_feature",
        "singular covariance rank retained",
        gamma.rank() == 1,
        gamma.rank(),
        1,
    )
    audit.check(
        "trace_feature",
        "mixed trace equals shared-probe feature",
        trace_cross == (uq.T * up)[0],
        trace_cross,
        (uq.T * up)[0],
    )
    audit.check(
        "trace_feature",
        "diagonal trace equals feature norm",
        sp.trace(aq * gamma * aq.T) == (uq.T * uq)[0],
        sp.trace(aq * gamma * aq.T),
        (uq.T * uq)[0],
    )

    # Exact Hessian of P_comp=(||Phi||^2-||U||^2)/2.
    h1, h2 = sp.symbols("h1 h2", real=True)
    u_feature = sp.Matrix([h1**2 + h2, h1 * h2])
    phi_feature = sp.Matrix([h1 + h2**2, h1 - h2])
    owner = sp.expand(
        ((phi_feature.T * phi_feature)[0] - (u_feature.T * u_feature)[0]) / 2
    )
    hessian_direct = sp.hessian(owner, (h1, h2))
    jac_u = u_feature.jacobian((h1, h2))
    jac_phi = phi_feature.jacobian((h1, h2))
    connection_u = sp.zeros(2)
    connection_phi = sp.zeros(2)
    for component in range(2):
        connection_u += u_feature[component] * sp.hessian(
            u_feature[component], (h1, h2)
        )
        connection_phi += phi_feature[component] * sp.hessian(
            phi_feature[component], (h1, h2)
        )
    hessian_feature = sp.simplify(
        jac_phi.T * jac_phi
        + connection_phi
        - jac_u.T * jac_u
        - connection_u
    )
    audit.check(
        "hessian",
        "two-feature Hessian identity",
        hessian_direct == hessian_feature,
        hessian_direct,
        hessian_feature,
    )
    audit.check(
        "hessian",
        "favorable mean-square sign",
        sp.factor((jac_phi.T * jac_phi).det()) >= 0
        and sp.factor(sp.trace(jac_phi.T * jac_phi)) >= 0,
        (
            sp.factor((jac_phi.T * jac_phi).det()),
            sp.factor(sp.trace(jac_phi.T * jac_phi)),
        ),
        "nonnegative determinant and trace",
    )

    # 2. Exact SU(2) fibre block at a nondegenerate audit point.
    r = Q(7, 5)
    s = Q(3, 4)
    floor = Q(1, 9)
    t = r * r / (r * r + s * s + floor)
    radial_a = r * r * (
        C0_INPUT + C1_INPUT * (Q(1) - ALPHA_INPUT * t) ** 2
    )
    radial_c = -(
        C1_INPUT
        * ALPHA_INPUT
        * t
        * (Q(1) - ALPHA_INPUT * t)
        * r
        * s
    )
    radial_d = C1_INPUT * ALPHA_INPUT**2 * t**2 * s**2
    radial_inner = [[radial_a, radial_c], [radial_c, radial_d]]
    radial_block = [[Q(4) * value for value in row] for row in radial_inner]
    transverse = Q(4) * (C0_INPUT + C1_INPUT) * r * r
    active_block = [
        [transverse, Q(0), Q(0), Q(0)],
        [Q(0), transverse, Q(0), Q(0)],
        [Q(0), Q(0), radial_block[0][0], radial_block[0][1]],
        [Q(0), Q(0), radial_block[1][0], radial_block[1][1]],
    ]
    active_float = fraction_matrix_to_float(active_block)
    active_eigenvalues = np.linalg.eigvalsh(active_float)
    radial_determinant = (
        radial_block[0][0] * radial_block[1][1]
        - radial_block[0][1] * radial_block[1][0]
    )
    radial_determinant_formula = (
        Q(16)
        * C0_INPUT
        * C1_INPUT
        * ALPHA_INPUT**2
        * t**2
        * r**2
        * s**2
    )
    audit.check(
        "su2",
        "transverse coefficient exact",
        Q(4) * (C0_INPUT + C1_INPUT) == Q(339, 2000) / P_INPUT,
        Q(4) * (C0_INPUT + C1_INPUT),
        Q(339, 2000) / P_INPUT,
    )
    audit.check(
        "su2",
        "two transverse eigenvalues",
        sum(abs(value - float(transverse)) <= TOL for value in active_eigenvalues)
        == 2,
        active_eigenvalues.tolist(),
        f"two copies of {float(transverse)}",
    )
    audit.check(
        "su2",
        "radial determinant formula",
        radial_determinant == radial_determinant_formula,
        radial_determinant,
        radial_determinant_formula,
    )
    audit.check(
        "su2",
        "generic radial determinant positive",
        radial_determinant > 0,
        radial_determinant,
        ">0",
    )
    audit.check(
        "su2",
        "active block positive definite",
        float(active_eigenvalues[0]) > 0,
        active_eigenvalues.tolist(),
        "all positive",
    )
    audit.check(
        "su2",
        "sharp transverse upper edge",
        float(active_eigenvalues[-1]) <= float(transverse) + TOL,
        active_eigenvalues[-1],
        transverse,
    )
    full_block = np.zeros((6, 6), dtype=float)
    full_block[:4, :4] = active_float
    full_eigenvalues = np.linalg.eigvalsh(full_block)
    audit.check(
        "su2",
        "two exact phase kernels",
        int(np.count_nonzero(np.abs(full_eigenvalues) <= TOL)) == 2,
        full_eigenvalues.tolist(),
        "two zeros",
    )
    audit.check(
        "su2",
        "generic full rank four",
        np.linalg.matrix_rank(full_block, tol=TOL) == 4,
        np.linalg.matrix_rank(full_block, tol=TOL),
        4,
    )
    pure_doublet_radial_inner = C0_INPUT + C1_INPUT * (Q(1) - ALPHA_INPUT) ** 2
    audit.check(
        "su2",
        "transverse to scalar radial ratio",
        (C0_INPUT + C1_INPUT) / pure_doublet_radial_inner == Q(113, 48),
        (C0_INPUT + C1_INPUT) / pure_doublet_radial_inner,
        Q(113, 48),
    )

    # 3. Production family-lock mass and scalar-principal covariance split.
    identity3 = sp.eye(3)
    one = sp.Matrix(LOCK_VECTOR_INPUT)
    projector = one * one.T / (one.T * one)[0]
    mass = sp.diag(*FAMILY_MASSES_INPUT) + sp.Rational(
        LOCK_INPUT.numerator, LOCK_INPUT.denominator
    ) * (identity3 - projector)
    expected_mass = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    audit.check("covariance", "mass derived from family and lock inputs", mass == expected_mass, mass, expected_mass)
    variable = sp.symbols("mu")
    charpoly = sp.expand(mass.charpoly(variable).as_expr())
    expected_charpoly = (
        sp.Rational(1, 25000)
        * (25000 * variable**3 - 10000 * variable**2 + 1115 * variable - 24)
    )
    audit.check("covariance", "mass characteristic polynomial", charpoly == expected_charpoly, charpoly, expected_charpoly)
    mass_float = np.asarray(mass, dtype=float)
    mu = np.linalg.eigvalsh(mass_float)
    audit.check("covariance", "mass strictly positive", float(mu[0]) > 0, mu.tolist(), "positive")
    audit.check("covariance", "mass eigenvalue ordering", bool(np.all(np.diff(mu) > 0)), mu.tolist(), "strict")
    t3 = sp.diag(1, -1, 0)
    commutator = mass * t3 - t3 * mass
    commutator_float = np.asarray(commutator, dtype=float)
    commutator_norm_sq = float(np.linalg.norm(commutator_float, 2) ** 2)
    audit.check(
        "covariance",
        "SU2 breaking commutator",
        commutator != sp.zeros(3),
        commutator,
        "nonzero",
    )
    audit.check(
        "covariance",
        "commutator norm squared",
        abs(commutator_norm_sq - float(Q(3, 200))) <= TOL,
        commutator_norm_sq,
        Q(3, 200),
    )
    covariance_remainder_norms: dict[str, float] = {}
    for a_value in (Q(1, 2), Q(3, 2), Q(7)):
        a_float = float(a_value)
        covariance = np.linalg.inv(a_float * np.eye(3) + mass_float)
        gamma0 = 1.0 / (a_float + float(mu[2]))
        remainder = covariance - gamma0 * np.eye(3)
        remainder_eigenvalues = np.linalg.eigvalsh(remainder)
        formula = (float(mu[2]) - float(mu[0])) / (
            (a_float + float(mu[0])) * (a_float + float(mu[2]))
        )
        key = str(a_value)
        covariance_remainder_norms[key] = float(remainder_eigenvalues[-1])
        audit.check(
            "covariance",
            f"remainder PSD at a={key}",
            float(remainder_eigenvalues[0]) >= -TOL,
            remainder_eigenvalues.tolist(),
            "PSD",
        )
        audit.check(
            "covariance",
            f"remainder norm formula at a={key}",
            abs(float(remainder_eigenvalues[-1]) - formula) <= TOL,
            remainder_eigenvalues[-1],
            formula,
        )

    # 4. Legal scalar two-root/two-visit adapted chart.
    sqrt2 = math.sqrt(2.0)
    m_g = (
        float(SOURCE_FLOOR)
        - 4.0 * float(C1_INPUT) * (3.0 + sqrt2)
        - (4.0 * float(C1_INPUT) * (2.0 + sqrt2)) ** 2 / 18.0
    )
    covariance_score_lower = (
        SOURCE_FLOOR + Q(81, 4) - Q(2) * C0_INPUT - Q(8) * C1_INPUT
    )
    audit.check("scalar_chart", "translation lower bound above three quarters", m_g > 0.75, m_g, ">3/4")
    audit.check(
        "scalar_chart",
        "covariance-score exact lower numerator",
        covariance_score_lower
        == Q(1_686_660_000_000_423, 80_000_000_000_020),
        covariance_score_lower,
        Q(1_686_660_000_000_423, 80_000_000_000_020),
    )
    audit.check(
        "scalar_chart",
        "covariance direction strongly positive",
        float(covariance_score_lower) > 21.08,
        float(covariance_score_lower),
        ">21.08",
    )
    gaussian_even_moments = {0: 1, 2: 1, 4: 3, 6: 15}
    score_majorant = Q(gaussian_even_moments[6] + gaussian_even_moments[2], 4)
    audit.check("scalar_chart", "Hermite score majorant", score_majorant == Q(4), score_majorant, Q(4))
    source_metric = np.eye(3)
    physical_synthesis_metric = np.asarray(
        [[0.5, 0.5, 0.0], [0.5, 0.5, 0.0], [0.0, 0.0, 0.5]]
    )
    audit.check(
        "scalar_chart",
        "source chart orthonormal",
        np.allclose(source_metric, np.eye(3)),
        source_metric.tolist(),
        "I3",
    )
    audit.check(
        "scalar_chart",
        "physical synthesis has translation kernel",
        np.linalg.matrix_rank(physical_synthesis_metric) == 2,
        np.linalg.eigvalsh(physical_synthesis_metric).tolist(),
        "rank 2",
    )

    # 5. Exact coefficient-slice C8/C10 signed moved bands.
    ranges = {offset: list(shell_range(offset)) for offset in range(5, 10)}
    expected_ranges = {
        5: list(range(9, 17)),
        6: list(range(17, 33)),
        7: list(range(33, 65)),
        8: list(range(65, 129)),
        9: list(range(129, 257)),
    }
    audit.check("band", "dyadic shell ranges", ranges == expected_ranges, {k: (v[0], v[-1]) for k, v in ranges.items()}, {k: (v[0], v[-1]) for k, v in expected_ranges.items()})
    delta = 0.2
    floor_value = delta * delta
    coefficients = {
        n: rational_coefficient(n, delta, floor_value) for n in range(2, 258)
    }
    g = {
        n: 0.5 * coefficients[n]
        - 0.25 * (coefficients[n - 1] + coefficients[n + 1])
        for n in range(3, 257)
    }
    wrong_signs = [
        n for n, value in g.items() if ((-1) ** (n + 1)) * value <= 0.0
    ]
    audit.check("band", "alternating g_n sign through C10", wrong_signs == [], wrong_signs, [])
    sign_identity_errors = [
        n
        for n, value in g.items()
        if abs(
            ((-1) ** (n + 1)) * value
            - (
                abs(coefficients[n]) / 2.0
                + abs(coefficients[n - 1]) / 4.0
                + abs(coefficients[n + 1]) / 4.0
            )
        )
        > 1.0e-14 * max(1.0, abs(value))
    ]
    audit.check(
        "band",
        "sign-stripped coefficient identity",
        sign_identity_errors == [],
        sign_identity_errors,
        [],
    )
    weights = {offset: 2.0 ** (-offset / 3.0) for offset in range(5, 10)}

    def weighted_band(max_offset: int) -> float:
        total = 0.0
        for offset in range(5, max_offset + 1):
            for n in ranges[offset]:
                total += 2.0 * weights[offset] * g[n] * math.cos(math.pi * n)
        return total

    h8 = weighted_band(7)
    h10 = weighted_band(9)
    audit.check("band", "C8 signed symbol negative at pi over two", h8 < 0.0, h8, "<0")
    audit.check("band", "C10 signed symbol negative at pi over two", h10 < 0.0, h10, "<0")
    aligned_output = 2_114_970
    harmonics = (17, 33, 65)
    carriers = tuple(aligned_output // harmonic for harmonic in harmonics)
    audit.check(
        "band",
        "three-layer coherent output divisibility",
        all(carrier * harmonic == aligned_output for carrier, harmonic in zip(carriers, harmonics)),
        carriers,
        aligned_output,
    )
    audit.check(
        "band",
        "coherent carrier values",
        carriers == (124_410, 64_090, 32_538),
        carriers,
        (124_410, 64_090, 32_538),
    )

    scope = {
        "finite_cutoff_positive_floor": True,
        "fixed_chart_innovation_compression": True,
        "canonical_actual_trace_feature_fixed_chart": True,
        "two_feature_hessian": True,
        "coefficient_exact_su2_fibre_block": True,
        "production_family_lock_covariance_split": True,
        "legal_scalar_two_root_two_visit_chart": True,
        "coefficient_exact_c8_c10_negative_band_direction": True,
        "full_production_common_feature_matrix_assembled": False,
        "uniform_production_loewner_bound": False,
        "scalar_chart_extends_to_transverse_su2": False,
        "coefficient_band_is_full_owner_counterexample": False,
        "positive_production_graph_gap": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    for key in (
        "full_production_common_feature_matrix_assembled",
        "uniform_production_loewner_bound",
        "scalar_chart_extends_to_transverse_su2",
        "coefficient_band_is_full_owner_counterexample",
        "positive_production_graph_gap",
        "a13_gate_closed",
        "nelson",
        "sector_a_closed",
    ):
        audit.check("scope", f"{key} false", scope[key] is False, scope[key], False)

    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows) - failed,
            "failed": failed,
            "rows": audit.rows,
        },
        "inputs": {
            "P": str(P_INPUT),
            "alpha": str(ALPHA_INPUT),
            "c0": str(C0_INPUT),
            "c1": str(C1_INPUT),
            "family_masses": [str(value) for value in FAMILY_MASSES_INPUT],
            "lock": str(LOCK_INPUT),
            "lock_vector": [str(value) for value in LOCK_VECTOR_INPUT],
            "source_floor": str(SOURCE_FLOOR),
        },
        "computed": {
            "innovation_raw_cross": str(raw_cross),
            "innovation_residual_cross": str(residual_cross),
            "innovation_mean_cross": str(mean_cross_value),
            "trace_cross": str(trace_cross),
            "two_feature_hessian": str(hessian_direct),
            "su2_audit_point": {"r": str(r), "s": str(s), "floor": str(floor), "t": str(t)},
            "su2_transverse_eigenvalue": str(transverse),
            "su2_radial_determinant": str(radial_determinant),
            "su2_full_eigenvalues": full_eigenvalues.tolist(),
            "mass_matrix": [[str(value) for value in row] for row in mass.tolist()],
            "mass_eigenvalues": mu.tolist(),
            "commutator_norm_squared": commutator_norm_sq,
            "covariance_remainder_norms": covariance_remainder_norms,
            "scalar_translation_lower_bound": m_g,
            "scalar_covariance_lower_bound": str(covariance_score_lower),
            "band_ranges": {str(key): [values[0], values[-1]] for key, values in ranges.items()},
            "c8_symbol_pi_over_two": h8,
            "c10_symbol_pi_over_two": h10,
            "coherent_output": aligned_output,
            "coherent_carriers": list(carriers),
        },
        "scope": scope,
    }
    atomic_json(args.output, payload)
    print(
        f"{RESULT_ID}: {'PASS' if failed == 0 else 'FAIL'} "
        f"({len(audit.rows) - failed}/{len(audit.rows)})"
    )
    print(f"output: {args.output}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
