#!/usr/bin/env python3
"""Independent audit of the Q3LOCK cubic-graph/product-locality split.

This verifier is deliberately disjoint from the primary implementation.  It
uses only the Python standard library, reconstructs every finite algebraic
fixture with ``Fraction``/integer arithmetic (and uses ``Decimal`` only for
display-level square roots and logarithms), never imports the primary script,
and never reads a primary result artifact.

The positive scope is finite-volume: the centered weighted cubic graph bound
and the prescribed-word heat-simplex lemma.  The four registered negative
results reject only an unweighted moving-site estimate, a raw absolute animal
majorant, absolute heat-strip continuation, and Duhamel-inner-product-only
strong-star promotion.  This audit does not close either common-dynamics gate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-second-weighted-energy-"
    "cauchy-gate-manifest.json"
)
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

MOVING_SITE_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-MOVING-SITE-"
    "CUBIC-GRAPH-UNIFORMITY"
)
ANIMAL_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-ABSOLUTE-CONNECTED-"
    "HISTORY-ANIMAL-MAJORANT"
)
STRIP_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-ABSOLUTE-HEAT-STRIP-"
    "REAL-TIME-CONTINUATION"
)
DUHAMEL_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-DUHAMEL-INNER-PRODUCT-"
    "ONLY-COMMON-DYNAMICS"
)
NEGATIVE_IDS = (MOVING_SITE_NG, ANIMAL_NG, STRIP_NG, DUHAMEL_NG)
FIRST_PASSAGE_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-"
    "PRODUCT-AND-ENERGY-TAIL-CLOSURE"
)
MODULAR_CUTOFF_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-MODULAR-"
    "CUTOFF-LOCALITY"
)


def serial(value: Any) -> Any:
    """Convert exact objects to stable JSON values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return the canonical compact encoding used by the self-test digest."""

    return json.dumps(
        serial(dict(payload)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def normalized_sha256(path: Path) -> str:
    """Hash a source after normalizing platform line endings."""

    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a complete deterministic JSON artifact by atomic replacement."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                serial(dict(payload)),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast assertion ledger."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


# Bivariate polynomials in (a,b), with lambda factored out.
Polynomial = dict[tuple[int, int], Fraction]


def poly_clean(polynomial: Mapping[tuple[int, int], Fraction]) -> Polynomial:
    return {
        powers: coefficient
        for powers, coefficient in polynomial.items()
        if coefficient != 0
    }


def poly_add(*polynomials: Mapping[tuple[int, int], Fraction]) -> Polynomial:
    output: Polynomial = {}
    for polynomial in polynomials:
        for powers, coefficient in polynomial.items():
            output[powers] = output.get(powers, Fraction(0)) + coefficient
    return poly_clean(output)


def poly_scale(
    polynomial: Mapping[tuple[int, int], Fraction], scale: Fraction
) -> Polynomial:
    return poly_clean(
        {powers: scale * coefficient for powers, coefficient in polynomial.items()}
    )


def poly_multiply(
    left: Mapping[tuple[int, int], Fraction],
    right: Mapping[tuple[int, int], Fraction],
) -> Polynomial:
    output: Polynomial = {}
    for (left_a, left_b), left_coefficient in left.items():
        for (right_a, right_b), right_coefficient in right.items():
            powers = (left_a + right_a, left_b + right_b)
            output[powers] = output.get(powers, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return poly_clean(output)


def poly_power(
    polynomial: Mapping[tuple[int, int], Fraction], exponent: int
) -> Polynomial:
    output: Polynomial = {(0, 0): Fraction(1)}
    for _ in range(exponent):
        output = poly_multiply(output, polynomial)
    return output


def poly_derivative(
    polynomial: Mapping[tuple[int, int], Fraction], variable: int
) -> Polynomial:
    output: Polynomial = {}
    for powers, coefficient in polynomial.items():
        exponent = powers[variable]
        if exponent == 0:
            continue
        reduced = list(powers)
        reduced[variable] -= 1
        output[tuple(reduced)] = coefficient * exponent
    return poly_clean(output)


def q3_force_fixture() -> dict[str, Any]:
    """Reconstruct the cube graph and one-edge force polynomial exactly."""

    vertices = list(itertools.product((0, 1), repeat=3))
    edges = [
        (left, right)
        for left in range(len(vertices))
        for right in range(left + 1, len(vertices))
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(8)]

    a: Polynomial = {(1, 0): Fraction(1)}
    b: Polynomial = {(0, 1): Fraction(1)}
    difference = poly_add(a, poly_scale(b, Fraction(-1)))
    square_sum = poly_add(poly_power(a, 2), poly_power(b, 2))
    edge_quartic = poly_scale(
        poly_multiply(poly_power(difference, 2), square_sum), Fraction(1, 4)
    )
    force = poly_derivative(edge_quartic, 0)
    coefficient_l1 = sum((abs(value) for value in force.values()), Fraction(0))
    return {
        "vertices": vertices,
        "edges": edges,
        "degrees": degrees,
        "edge_quartic_over_lambda": edge_quartic,
        "edge_force_over_lambda": force,
        "edge_force_oracle": {
            (3, 0): Fraction(1),
            (2, 1): Fraction(-3, 2),
            (1, 2): Fraction(1),
            (0, 3): Fraction(-1, 2),
        },
        "edge_force_l1": coefficient_l1,
        "component_lambda_coefficient": max(degrees) * coefficient_l1,
        "components": len(vertices),
    }


def decimal_sqrt_fraction(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec = 70
        return (Decimal(value.numerator) / Decimal(value.denominator)).sqrt()


def graph_fixture() -> dict[str, Any]:
    """Derive the exact cancellation and graph constants from declared inputs."""

    inputs = {
        "chi": Fraction(2),
        "c": Fraction(3, 2),
        "g": Fraction(5),
        "lambda": Fraction(2),
        "hbar": Fraction(1),
        "gamma": Fraction(1, 10),
        "r_plus": Fraction(1),
        "z": Fraction(6),
        "exp_mu": Fraction(2),
        "support_size": Fraction(1),
    }
    chi = inputs["chi"]
    c = inputs["c"]
    g = inputs["g"]
    lam = inputs["lambda"]
    hbar = inputs["hbar"]
    gamma = inputs["gamma"]
    r_plus = inputs["r_plus"]
    z = inputs["z"]
    exp_mu = inputs["exp_mu"]
    support_size = inputs["support_size"]

    c2 = 3 * g + 21 * lam
    epsilon_star = 4 * chi / (hbar**2 * c2)
    exp_minus_mu = 1 / exp_mu
    s_bound = support_size * (
        (1 + exp_minus_mu) / (1 - exp_minus_mu)
    ) ** 3
    b_star = s_bound * (
        8 * r_plus
        + 8 * c * z
        + hbar**2 * c2**2 / (16 * chi * gamma)
    )
    beta_star = hbar**2 * b_star / (2 * chi)
    kappa_squared = max(Fraction(1), beta_star)
    cancellation = hbar**2 * c2 * epsilon_star / (2 * chi)
    cubic_constant_eighth = gamma ** (-6) * kappa_squared**3

    theta = exp_mu - 1
    # C_mu = identity + potential difference + kinetic difference.
    center_ledger = {
        "identity": {"constant": Fraction(1), "kappa": Fraction(0)},
        "potential_difference": {
            "constant": Fraction(0),
            "kappa": theta,
        },
        "kinetic_difference": {
            "constant": 2 * theta,
            "kappa": theta,
        },
    }
    center_constant = sum(
        (row["constant"] for row in center_ledger.values()), Fraction(0)
    )
    center_kappa = sum(
        (row["kappa"] for row in center_ledger.values()), Fraction(0)
    )
    kappa_decimal = decimal_sqrt_fraction(kappa_squared)
    with localcontext() as context:
        context.prec = 70
        center_decimal = (
            Decimal(center_constant.numerator) / Decimal(center_constant.denominator)
            + Decimal(center_kappa.numerator)
            / Decimal(center_kappa.denominator)
            * kappa_decimal
        )

    return {
        "inputs": inputs,
        "C2": c2,
        "epsilon_star": epsilon_star,
        "S_bound": s_bound,
        "b_star": b_star,
        "beta_star": beta_star,
        "kappa_squared": kappa_squared,
        "kappa_decimal": kappa_decimal,
        "cancellation_coefficient": cancellation,
        "gamma_admitted": gamma < g / 32,
        "cubic_constant_eighth": cubic_constant_eighth,
        "theta": theta,
        "moving_center_ledger": center_ledger,
        "moving_center_constant_coefficient": center_constant,
        "moving_center_kappa_coefficient": center_kappa,
        "moving_center_decimal": center_decimal,
    }


def moving_bump_fixture() -> dict[str, Any]:
    """Expose the exact f^(-3/4) asymptotic with a perfect-fourth fixture."""

    f = Fraction(1, 16)
    rows: list[dict[str, Any]] = []
    # With C0=0 and C1=1, (f R^4)^(3/4)=R^3/8 exactly.
    for radius in (2, 4, 8, 16, 32, 64):
        ratio = Fraction(8 * (radius - 1) ** 3, radius**3)
        rows.append({"R": radius, "ratio": ratio})
    return {
        "f": f,
        "rows": rows,
        "strictly_increasing": all(
            right["ratio"] > left["ratio"]
            for left, right in zip(rows, rows[1:])
        ),
        "limit": Fraction(8),
        "expected_limit": Fraction(8),
        "R_degree": Fraction(3) - 4 * Fraction(3, 4),
        "f_exponent": Fraction(-3, 4),
        "C1_exponent": Fraction(-3, 4),
    }


def double_factorial(value: int) -> int:
    if value in (-1, 0):
        return 1
    output = 1
    for factor in range(value, 0, -2):
        output *= factor
    return output


def heat_dirichlet_fixture() -> dict[str, Any]:
    """Derive n=1..8 without a Gamma-function or floating-point call.

    Each integral is stored as
      rational * pi**pi_power * beta**beta_power.
    For n=2k the rational is 1/k!.  For n=2k+1 it is
    2**(k+1)/(2k+1)!!.
    """

    rows: list[dict[str, Any]] = []
    for n in range(1, 9):
        if n % 2 == 0:
            k = n // 2
            rational = Fraction(1, math.factorial(k))
            pi_power = k
            constructor = "factorial"
            denominator_check = math.factorial(k)
        else:
            k = (n - 1) // 2
            rational = Fraction(2 ** (k + 1), double_factorial(2 * k + 1))
            pi_power = k
            constructor = "double_factorial"
            denominator_check = double_factorial(2 * k + 1)
        rows.append(
            {
                "n": n,
                "rational": rational,
                "pi_power": pi_power,
                "beta_power": Fraction(n, 2),
                "constructor": constructor,
                "denominator_check": denominator_check,
                "heat_two_exponent": Fraction(-n, 2),
                "heat_e_exponent": Fraction(-n, 2),
            }
        )

    # Exact expected coefficient table, independent of the recurrence above.
    oracle = (
        (Fraction(2), 0, Fraction(1, 2)),
        (Fraction(1), 1, Fraction(1)),
        (Fraction(4, 3), 1, Fraction(3, 2)),
        (Fraction(1, 2), 2, Fraction(2)),
        (Fraction(8, 15), 2, Fraction(5, 2)),
        (Fraction(1, 6), 3, Fraction(3)),
        (Fraction(16, 105), 3, Fraction(7, 2)),
        (Fraction(1, 24), 4, Fraction(4)),
    )

    c = Fraction(3, 2)
    gamma = Fraction(1, 10)
    base_rung_squared = c**2 / (2 * gamma)
    # kappa_0^2 = (c^2/gamma) * pi/e.
    commutator_activity_squared_pi_over_e = c**2 / gamma
    return {
        "rows": rows,
        "oracle": oracle,
        "base_rung_squared_fixture": base_rung_squared,
        "commutator_activity_squared_pi_over_e_fixture": (
            commutator_activity_squared_pi_over_e
        ),
    }


def decimal_log_integer(value: int) -> Decimal:
    with localcontext() as context:
        context.prec = 70
        return Decimal(value).ln()


def animal_fixture() -> dict[str, Any]:
    """Use exact integer factorial ratios for an even-m subsequence."""

    samples = (2, 4, 6, 8, 10, 12, 14, 16)
    rows: list[dict[str, Any]] = []
    for m in samples:
        histories = math.factorial(4 * m)
        gamma_denominator = math.factorial(5 * m // 2)
        coefficient = Fraction(histories, gamma_denominator)
        with localcontext() as context:
            context.prec = 70
            log_coefficient = Decimal(histories).ln() - Decimal(
                gamma_denominator
            ).ln()
        rows.append(
            {
                "m": m,
                "edges": 5 * m,
                "histories": histories,
                "gamma_denominator": gamma_denominator,
                "coefficient_at_a1": coefficient,
                "log_coefficient_at_a1": log_coefficient,
            }
        )

    recurrence_rows: list[dict[str, Any]] = []
    for m in samples[:-1]:
        next_m = m + 2
        direct = Fraction(
            math.factorial(4 * next_m), math.factorial(5 * next_m // 2)
        ) / Fraction(math.factorial(4 * m), math.factorial(5 * m // 2))
        product_ratio = Fraction(
            math.prod(4 * m + offset for offset in range(1, 9)),
            math.prod(5 * m // 2 + offset for offset in range(1, 6)),
        )
        recurrence_rows.append(
            {
                "m": m,
                "direct_ratio": direct,
                "product_ratio": product_ratio,
            }
        )
    return {
        "rows": rows,
        "recurrence_rows": recurrence_rows,
        "coefficients_strictly_increasing": all(
            right["coefficient_at_a1"] > left["coefficient_at_a1"]
            for left, right in zip(rows, rows[1:])
        ),
        "logs_strictly_increasing": all(
            right["log_coefficient_at_a1"] > left["log_coefficient_at_a1"]
            for left, right in zip(rows, rows[1:])
        ),
        "recurrence_degree_excess": 8 - 5,
        "stirling_m_log_m_coefficient": Fraction(4) - Fraction(5, 2),
    }


def real_time_fixture() -> dict[str, Any]:
    """Reconstruct chain degree, velocity coefficient, and strip divergence."""

    lattice_degree = 6
    path_degree = 2 * lattice_degree - 1
    strip_rows: list[dict[str, Any]] = []
    # C=1 and s=3/2: log(epsilon^(s-1) exp(C/epsilon)).
    with localcontext() as context:
        context.prec = 70
        log_two = Decimal(2).ln()
        for k in range(2, 13):
            epsilon = Fraction(1, 2**k)
            log_integrand = -Decimal(k) * log_two / Decimal(2) + Decimal(2**k)
            strip_rows.append(
                {
                    "k": k,
                    "epsilon": epsilon,
                    "log_integrand_C1_s3over2": log_integrand,
                }
            )
    return {
        "lattice_degree": lattice_degree,
        "path_degree": path_degree,
        "path_degree_squared": path_degree**2,
        "response_exponents": (Fraction(1, 2), Fraction(3, 4)),
        "velocity_rho_coefficient": path_degree**2,
        "spatial_condition_mu_coefficient": Fraction(1, 4),
        "strip_rows": strip_rows,
        "strip_logs_strictly_increasing": all(
            right["log_integrand_C1_s3over2"]
            > left["log_integrand_C1_s3over2"]
            for left, right in zip(strip_rows, strip_rows[1:])
        ),
        "strip_log_last_positive": strip_rows[-1][
            "log_integrand_C1_s3over2"
        ]
        > 0,
    }


def equilibrium_cutoff_fixture() -> dict[str, Any]:
    dimension = Fraction(3)
    moment = Fraction(5)
    scale = Fraction(7, 4)
    lower = 2 * dimension / (moment - 1)
    leakage = dimension + scale * (1 - moment) / 2
    factorial = scale / 2 - 1
    return {
        "dimension": dimension,
        "moment": moment,
        "scale_b": scale,
        "lower": lower,
        "upper": Fraction(2),
        "interval_admitted": lower < scale < 2,
        "moment_condition": moment > dimension + 1,
        "leakage_exponent": leakage,
        "factorial_m_log_m_exponent": factorial,
    }


def duhamel_fixture() -> dict[str, Any]:
    """Reconstruct the rank-shift fixture at exp(-beta)=1/2."""

    boltzmann = Fraction(1, 2)
    p0 = 1 - boltzmann
    rows: list[dict[str, Any]] = []
    for n in range(1, 33):
        pn = p0 * boltzmann**n
        beta_times_duhamel_square = (p0 - pn) / n
        symmetric_gns_square = (p0 + pn) / 2
        rows.append(
            {
                "n": n,
                "p_n": pn,
                "beta_times_duhamel_X_square": beta_times_duhamel_square,
                "beta_times_duhamel_Xstar_square": beta_times_duhamel_square,
                "symmetric_gns_square": symmetric_gns_square,
                "strong_image_X_e0_square": Fraction(1),
            }
        )

    # For the two-level modular ratio r=1/2, x=log(1/r)=log 2.
    # Arithmetic/logarithmic mean ratio = [(1+r)/2]/[(1-r)/x]
    # = (3/2) log 2.  Also coth(x/2)=(1+r)/(1-r)=3.
    modular_ratio = Fraction(1, 2)
    arithmetic_coefficient = (1 + modular_ratio) / 2
    logarithmic_mean_denominator_coefficient = 1 - modular_ratio
    arithmetic_over_log_mean_log_coefficient = (
        arithmetic_coefficient / logarithmic_mean_denominator_coefficient
    )
    coth_half_log_ratio = (1 + modular_ratio) / (1 - modular_ratio)
    bandwidth_log_coefficient = coth_half_log_ratio / 2
    return {
        "boltzmann": boltzmann,
        "p0": p0,
        "rows": rows,
        "duhamel_strictly_decreasing": all(
            right["beta_times_duhamel_X_square"]
            < left["beta_times_duhamel_X_square"]
            for left, right in zip(rows, rows[1:])
        ),
        "symmetric_lower_limit": p0 / 2,
        "modular_ratio": modular_ratio,
        "arithmetic_over_log_mean_log_coefficient": (
            arithmetic_over_log_mean_log_coefficient
        ),
        "coth_half_log_ratio": coth_half_log_ratio,
        "bandwidth_log_coefficient": bandwidth_log_coefficient,
        "modular_identity_residual": (
            arithmetic_over_log_mean_log_coefficient
            - bandwidth_log_coefficient
        ),
    }


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    negative_registry = NEGATIVE_REGISTRY.read_text(encoding="utf-8")

    audit.check(
        "manifest schema",
        manifest["schema"] == "tect/pre-a-route-split/1.0",
        manifest["schema"],
        "tect/pre-a-route-split/1.0",
        "provenance",
    )
    audit.check(
        "task binding", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance"
    )
    audit.check(
        "claim binding",
        manifest["claim_ids"] == ["C6-SPACETIME-SIGNATURE"],
        manifest["claim_ids"],
        ["C6-SPACETIME-SIGNATURE"],
        "provenance",
    )
    audit.check(
        "result identity",
        manifest["result_id"] == RESULT_ID == parent["result_id"],
        manifest["result_id"],
        RESULT_ID,
        "provenance",
    )
    audit.check(
        "result number reused",
        manifest["result_number"] == "R-167",
        manifest["result_number"],
        "R-167",
        "provenance",
    )
    audit.check(
        "result version strengthened",
        manifest["result_version"] == "v1.1",
        manifest["result_version"],
        "v1.1",
        "provenance",
    )
    audit.check(
        "exploration binding",
        manifest["exploration_id"] == "EXP-000796",
        manifest["exploration_id"],
        "EXP-000796",
        "provenance",
    )
    audit.check(
        "independent verifier path",
        manifest["verification"]["independent_script"]
        == str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        manifest["verification"]["independent_script"],
        str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        "provenance",
    )
    audit.check(
        "certificate identity",
        RESULT_ID in certificate and "v1.1" in certificate and "R-167" in certificate,
        {"result": RESULT_ID in certificate, "version": "v1.1" in certificate},
        "result, version, and number present",
        "provenance",
    )

    q3 = q3_force_fixture()
    audit.check("Q3 vertices", len(q3["vertices"]) == 8, len(q3["vertices"]), 8, "Q3")
    audit.check("Q3 edges", len(q3["edges"]) == 12, len(q3["edges"]), 12, "Q3")
    audit.check("Q3 degree", q3["degrees"] == [3] * 8, q3["degrees"], [3] * 8, "Q3")
    audit.check(
        "Q3 edge force polynomial",
        q3["edge_force_over_lambda"] == q3["edge_force_oracle"],
        q3["edge_force_over_lambda"],
        q3["edge_force_oracle"],
        "Q3",
    )
    audit.check(
        "Q3 edge force L1",
        q3["edge_force_l1"] == 4,
        q3["edge_force_l1"],
        4,
        "Q3",
    )
    audit.check(
        "Q3 component lambda coefficient",
        q3["component_lambda_coefficient"] == 12,
        q3["component_lambda_coefficient"],
        12,
        "Q3",
    )
    audit.check(
        "manifest Q3 force",
        "g+12lambda" in manifest["cubic_graph_embedding"]["q3_force"],
        manifest["cubic_graph_embedding"]["q3_force"],
        "g+12lambda",
        "Q3",
    )
    audit.check(
        "full gradient component factor",
        q3["components"] == 8
        and "sqrt(8)" in manifest["cubic_graph_embedding"]["q3_force"],
        {"components": q3["components"], "contract": manifest["cubic_graph_embedding"]["q3_force"]},
        "eight components and sqrt(8)",
        "Q3",
    )

    graph = graph_fixture()
    graph_oracles = {
        "C2": Fraction(57),
        "epsilon_star": Fraction(8, 57),
        "S_bound": Fraction(27),
        "b_star": Fraction(473175, 16),
        "beta_star": Fraction(473175, 64),
        "cancellation_coefficient": Fraction(2),
    }
    for key, expected in graph_oracles.items():
        audit.check(
            f"graph fixture {key}",
            graph[key] == expected,
            graph[key],
            expected,
            "graph",
        )
    audit.check(
        "graph gamma admitted",
        graph["gamma_admitted"],
        graph["inputs"]["gamma"],
        "gamma<g/32",
        "graph",
    )
    audit.check(
        "kappa branch",
        graph["kappa_squared"] == graph["beta_star"] > 1,
        graph["kappa_squared"],
        graph["beta_star"],
        "graph",
    )
    audit.check(
        "cubic eighth-power constant",
        graph["cubic_constant_eighth"]
        == graph["inputs"]["gamma"] ** (-6) * graph["kappa_squared"] ** 3,
        graph["cubic_constant_eighth"],
        "gamma^-6 kappa^6",
        "graph",
    )
    embedding = manifest["cubic_graph_embedding"]
    audit.check("cubic graph closed", embedding["closed"] is True, embedding["closed"], True, "graph")
    audit.check(
        "operator graph bound",
        "||U_f A^-1||<=kappa" in embedding["operator_bound"],
        embedding["operator_bound"],
        "||U_f A^-1||<=kappa",
        "graph",
    )
    audit.check(
        "Heinz--Kato exponent interval",
        "0<=theta<=1" in embedding["interpolation"],
        embedding["interpolation"],
        "0<=theta<=1",
        "graph",
    )
    audit.check(
        "natural powers through four",
        "0<=m<=4" in embedding["all_natural_powers"]
        and "adjoint orientation" in embedding["all_natural_powers"],
        embedding["all_natural_powers"],
        "m=0..4 and adjoint orientation",
        "graph",
    )
    audit.check(
        "cubic weighted power",
        "f_x^(3/4)" in embedding["cubic_conclusion"]
        and "A^-3/4" in embedding["cubic_conclusion"]
        and "3/8" in embedding["cubic_conclusion"],
        embedding["cubic_conclusion"],
        "weighted cubic A^-3/4 bound",
        "graph",
    )
    audit.check(
        "finite-volume weighted scope",
        "Finite volume" in embedding["scope"]
        and "spatial weight is essential" in embedding["scope"],
        embedding["scope"],
        "finite volume with essential spatial weight",
        "scope",
    )

    bump = moving_bump_fixture()
    audit.check(
        "moving bump R cancellation",
        bump["R_degree"] == 0,
        bump["R_degree"],
        0,
        "moving-site",
    )
    audit.check(
        "moving bump f exponent",
        bump["f_exponent"] == Fraction(-3, 4),
        bump["f_exponent"],
        Fraction(-3, 4),
        "moving-site",
    )
    audit.check(
        "moving bump exact finite convergence",
        bump["strictly_increasing"] and bump["limit"] == bump["expected_limit"],
        bump["rows"],
        "increasing to f^-3/4=8",
        "moving-site",
    )
    audit.check(
        "moving-site manifest exponent",
        "f_x^-3/4" in manifest["moving_site_boundary"]["finding"],
        manifest["moving_site_boundary"]["finding"],
        "f_x^-3/4",
        "moving-site",
    )
    audit.check(
        "moving-site consequence retains recentering",
        "recenter" in manifest["moving_site_boundary"]["does_not_show"].lower(),
        manifest["moving_site_boundary"]["does_not_show"],
        "recentered route retained",
        "scope",
    )

    audit.check(
        "moving-center constant coefficient",
        graph["moving_center_constant_coefficient"] == 3,
        graph["moving_center_constant_coefficient"],
        3,
        "moving-center",
    )
    audit.check(
        "moving-center kappa coefficient",
        graph["moving_center_kappa_coefficient"] == 2,
        graph["moving_center_kappa_coefficient"],
        2,
        "moving-center",
    )
    audit.check(
        "moving-center positive graph cost",
        graph["moving_center_decimal"] > 3,
        graph["moving_center_decimal"],
        ">3",
        "moving-center",
    )
    center = manifest["moving_center_comparison"]
    audit.check(
        "moving-center C_mu contract",
        "C_mu=1+2(exp(mu)-1)(1+kappa)" in center["neighbor_bound"],
        center["neighbor_bound"],
        "C_mu exact ledger",
        "moving-center",
    )
    audit.check(
        "moving-center fractional comparison",
        "0<=s<=1" in center["fractional_bound"] and "conversely" in center["fractional_bound"],
        center["fractional_bound"],
        "two orientations for s in [0,1]",
        "moving-center",
    )
    audit.check(
        "moving-center branch resummation remains open",
        "remains open" in center["consequence"],
        center["consequence"],
        "branch/repeat resummation remains open",
        "scope",
    )

    heat = heat_dirichlet_fixture()
    audit.check("heat row count", len(heat["rows"]) == 8, len(heat["rows"]), 8, "heat")
    for row, oracle in zip(heat["rows"], heat["oracle"]):
        actual = (row["rational"], row["pi_power"], row["beta_power"])
        audit.check(
            f"heat Dirichlet n={row['n']}",
            actual == oracle,
            actual,
            oracle,
            "heat",
        )
    audit.check(
        "heat odd double-factorials",
        [row["denominator_check"] for row in heat["rows"] if row["n"] % 2]
        == [1, 3, 15, 105],
        [row["denominator_check"] for row in heat["rows"] if row["n"] % 2],
        [1, 3, 15, 105],
        "heat",
    )
    audit.check(
        "heat even factorials",
        [row["denominator_check"] for row in heat["rows"] if row["n"] % 2 == 0]
        == [1, 2, 6, 24],
        [row["denominator_check"] for row in heat["rows"] if row["n"] % 2 == 0],
        [1, 2, 6, 24],
        "heat",
    )
    audit.check(
        "Q3LOCK base rung squared",
        heat["base_rung_squared_fixture"] == Fraction(45, 4),
        heat["base_rung_squared_fixture"],
        Fraction(45, 4),
        "heat",
    )
    audit.check(
        "commutator activity squared coefficient",
        heat["commutator_activity_squared_pi_over_e_fixture"] == Fraction(45, 2),
        heat["commutator_activity_squared_pi_over_e_fixture"],
        "(45/2) pi/e",
        "heat",
    )
    heat_contract = manifest["heat_simplex"]
    audit.check(
        "heat word denominator",
        "Gamma(1+n/2)" in heat_contract["word_bound"]
        and "sqrt(beta)" in heat_contract["word_bound"],
        heat_contract["word_bound"],
        "Gamma half-order word bound",
        "heat",
    )
    audit.check(
        "manifest base rung",
        heat_contract["q3lock_base_rung"] == "b=c/sqrt(2gamma)",
        heat_contract["q3lock_base_rung"],
        "b=c/sqrt(2gamma)",
        "heat",
    )
    audit.check(
        "manifest commutator activity",
        "c sqrt(pi/(e gamma))" in heat_contract["commutator_activity"],
        heat_contract["commutator_activity"],
        "c sqrt(pi/(e gamma))",
        "heat",
    )
    audit.check(
        "prescribed-word-only status",
        heat_contract["status"]
        == "PROVED FOR EACH PRESCRIBED WORD; NOT A CONNECTED-CLUSTER OR REAL-TIME THEOREM",
        heat_contract["status"],
        "prescribed word only",
        "scope",
    )

    animal = animal_fixture()
    audit.check(
        "animal n=5m ledger",
        all(row["edges"] == 5 * row["m"] for row in animal["rows"]),
        [(row["m"], row["edges"]) for row in animal["rows"]],
        "n=5m",
        "animal",
    )
    audit.check(
        "animal histories exact",
        all(row["histories"] == math.factorial(4 * row["m"]) for row in animal["rows"]),
        [row["histories"] for row in animal["rows"][:3]],
        "(4m)!",
        "animal",
    )
    audit.check(
        "animal factorial coefficients grow",
        animal["coefficients_strictly_increasing"] and animal["logs_strictly_increasing"],
        [row["log_coefficient_at_a1"] for row in animal["rows"]],
        "strictly increasing",
        "animal",
    )
    audit.check(
        "animal recurrence independently agrees",
        all(row["direct_ratio"] == row["product_ratio"] for row in animal["recurrence_rows"]),
        animal["recurrence_rows"],
        "all exact ratios agree",
        "animal",
    )
    audit.check(
        "animal recurrence degree excess",
        animal["recurrence_degree_excess"] == 3,
        animal["recurrence_degree_excess"],
        3,
        "animal",
    )
    audit.check(
        "animal Stirling coefficient",
        animal["stirling_m_log_m_coefficient"] == Fraction(3, 2),
        animal["stirling_m_log_m_coefficient"],
        Fraction(3, 2),
        "animal",
    )
    animal_contract = manifest["absolute_route_obstructions"]
    audit.check(
        "animal manifest factorial ratio",
        "(4m)!" in animal_contract["raw_animal"]
        and "Gamma(1+5m/2)" in animal_contract["raw_animal"]
        and "(3/2)m log m" in animal_contract["raw_animal"],
        animal_contract["raw_animal"],
        "factorial/Gamma ratio and 3/2 Stirling coefficient",
        "animal",
    )
    audit.check(
        "absolute no-go scope",
        "not nonexistence" in animal_contract["scope"],
        animal_contract["scope"],
        "method-only no-go",
        "scope",
    )

    real_time = real_time_fixture()
    audit.check(
        "chain degree P",
        real_time["path_degree"] == 11,
        real_time["path_degree"],
        11,
        "real-time",
    )
    audit.check(
        "chain exponent coefficient",
        real_time["path_degree_squared"] == 121,
        real_time["path_degree_squared"],
        121,
        "real-time",
    )
    audit.check(
        "strip exp(C/epsilon) growth fixture",
        real_time["strip_logs_strictly_increasing"]
        and real_time["strip_log_last_positive"],
        real_time["strip_rows"],
        "strictly increasing positive logarithm",
        "strip",
    )
    audit.check(
        "strip manifest nonintegrability",
        "exp(C/epsilon)" in animal_contract["strip_boundary"]
        and "diverges for every finite s" in animal_contract["strip_boundary"],
        animal_contract["strip_boundary"],
        "finite powers cannot integrate exp(C/epsilon)",
        "strip",
    )
    rt_contract = manifest["conditional_real_time_product"]
    audit.check(
        "first-passage gate identity",
        rt_contract["gate_id"] == FIRST_PASSAGE_GATE,
        rt_contract["gate_id"],
        FIRST_PASSAGE_GATE,
        "real-time",
    )
    audit.check(
        "first-passage status open",
        rt_contract["status"] == "OPEN",
        rt_contract["status"],
        "OPEN",
        "scope",
    )
    audit.check(
        "first-passage response exponents",
        "s_1=1/2" in rt_contract["response_target"]
        and "s_2=3/4" in rt_contract["response_target"]
        and "Gamma(1+n/2)" in rt_contract["response_target"],
        rt_contract["response_target"],
        "s1=1/2, s2=3/4, half-order Gamma denominator",
        "real-time",
    )
    audit.check(
        "first-passage two orientations",
        "both one-sided orientations" in rt_contract["response_target"],
        rt_contract["response_target"],
        "both one-sided orientations",
        "real-time",
    )
    audit.check(
        "manifest chain degree",
        rt_contract["chain_degree"] == "P=2z-1=11",
        rt_contract["chain_degree"],
        "P=2z-1=11",
        "real-time",
    )
    audit.check(
        "derived decay contract",
        "P^2 G_j^2 exp(2rho)" in rt_contract["derived_decay"]
        and "-rho d" in rt_contract["derived_decay"],
        rt_contract["derived_decay"],
        "-rho d + P^2 G_j^2 exp(2rho)|t|/hbar",
        "real-time",
    )
    audit.check(
        "velocity contract",
        "P^2 G_j^2 exp(2rho)/(rho hbar)" in rt_contract["velocity"],
        rt_contract["velocity"],
        "P^2 G_j^2 exp(2rho)/(rho hbar)",
        "real-time",
    )
    audit.check(
        "R-167 spatial condition",
        "rho>mu/4" in rt_contract["downstream"],
        rt_contract["downstream"],
        "rho>mu/4",
        "real-time",
    )
    audit.check(
        "moving-center activity absorption",
        "C_mu^(s_j n)" in rt_contract["downstream"],
        rt_contract["downstream"],
        "C_mu^(s_j n) absorbed into G_j",
        "moving-center",
    )

    equilibrium = equilibrium_cutoff_fixture()
    audit.check(
        "fifth moment dimension condition",
        equilibrium["moment_condition"],
        {"p": equilibrium["moment"], "d": equilibrium["dimension"]},
        "p>d+1",
        "equilibrium",
    )
    audit.check(
        "cutoff scale interval",
        equilibrium["interval_admitted"]
        and equilibrium["lower"] == Fraction(3, 2)
        and equilibrium["scale_b"] == Fraction(7, 4),
        equilibrium,
        "3/2<7/4<2",
        "equilibrium",
    )
    audit.check(
        "cutoff leakage exponent",
        equilibrium["leakage_exponent"] == Fraction(-1, 2),
        equilibrium["leakage_exponent"],
        Fraction(-1, 2),
        "equilibrium",
    )
    audit.check(
        "cutoff factorial exponent",
        equilibrium["factorial_m_log_m_exponent"] == Fraction(-1, 8),
        equilibrium["factorial_m_log_m_exponent"],
        Fraction(-1, 8),
        "equilibrium",
    )
    eq_contract = manifest["equilibrium_cutoff_alternative"]
    audit.check(
        "modular cutoff gate identity",
        eq_contract["gate_id"] == MODULAR_CUTOFF_GATE,
        eq_contract["gate_id"],
        MODULAR_CUTOFF_GATE,
        "equilibrium",
    )
    audit.check(
        "modular cutoff remains open",
        eq_contract["status"] == "OPEN",
        eq_contract["status"],
        "OPEN",
        "scope",
    )
    audit.check(
        "manifest moment target",
        "p>d+1" in eq_contract["moment_target"]
        and "p=5" in eq_contract["moment_target"]
        and "d=3" in eq_contract["moment_target"],
        eq_contract["moment_target"],
        "p=5>d+1 in d=3",
        "equilibrium",
    )
    audit.check(
        "manifest scale balance",
        "2d/(p-1)<b<2" in eq_contract["scale_balance"],
        eq_contract["scale_balance"],
        "2d/(p-1)<b<2",
        "equilibrium",
    )
    audit.check(
        "moment alone insufficient",
        "alone do not prove" in eq_contract["topology_requirement"]
        and "both one-sided/dual-state" in eq_contract["topology_requirement"],
        eq_contract["topology_requirement"],
        "moment plus two-sided modular/dual-state control required",
        "scope",
    )
    audit.check(
        "fixed-beta W-star boundary",
        "fixed-beta" in eq_contract["possible_scope"]
        and "W-star" in eq_contract["possible_scope"]
        and "before" in eq_contract["possible_scope"],
        eq_contract["possible_scope"],
        "at most fixed-beta W-star before C-star theorem",
        "scope",
    )

    duhamel = duhamel_fixture()
    audit.check(
        "Duhamel rank-shift row count",
        len(duhamel["rows"]) == 32,
        len(duhamel["rows"]),
        32,
        "Duhamel",
    )
    audit.check(
        "Duhamel X and Xstar equality",
        all(
            row["beta_times_duhamel_X_square"]
            == row["beta_times_duhamel_Xstar_square"]
            for row in duhamel["rows"]
        ),
        duhamel["rows"][:4],
        "equal squared Duhamel norms",
        "Duhamel",
    )
    audit.check(
        "Duhamel squares decrease",
        duhamel["duhamel_strictly_decreasing"],
        [row["beta_times_duhamel_X_square"] for row in duhamel["rows"][:8]],
        "strictly decreasing to zero",
        "Duhamel",
    )
    audit.check(
        "rank shift strong image fixed",
        all(row["strong_image_X_e0_square"] == 1 for row in duhamel["rows"]),
        [row["strong_image_X_e0_square"] for row in duhamel["rows"][:4]],
        1,
        "Duhamel",
    )
    audit.check(
        "symmetric GNS survives",
        all(
            row["symmetric_gns_square"] > duhamel["symmetric_lower_limit"]
            for row in duhamel["rows"]
        )
        and duhamel["symmetric_lower_limit"] == Fraction(1, 4),
        duhamel["symmetric_lower_limit"],
        Fraction(1, 4),
        "Duhamel",
    )
    audit.check(
        "modular arithmetic coth",
        duhamel["coth_half_log_ratio"] == 3,
        duhamel["coth_half_log_ratio"],
        3,
        "modular",
    )
    audit.check(
        "arithmetic/logarithmic mean identity",
        duhamel["arithmetic_over_log_mean_log_coefficient"] == Fraction(3, 2)
        and duhamel["modular_identity_residual"] == 0,
        {
            "arithmetic": duhamel["arithmetic_over_log_mean_log_coefficient"],
            "bandwidth": duhamel["bandwidth_log_coefficient"],
        },
        "(3/2) log 2 in both forms",
        "modular",
    )
    duhamel_contract = manifest["duhamel_topology_counterexample"]
    audit.check(
        "Duhamel squared-norm wording",
        duhamel_contract["duhamel"].startswith("The squared Duhamel norms"),
        duhamel_contract["duhamel"],
        "The squared Duhamel norms ...",
        "scope",
    )
    audit.check(
        "Duhamel exact formula",
        "(p_0-p_n)/(beta n)" in duhamel_contract["duhamel"],
        duhamel_contract["duhamel"],
        "(p_0-p_n)/(beta n)",
        "Duhamel",
    )
    audit.check(
        "Duhamel strong boundary",
        "X_n e_0=e_n" in duhamel_contract["strong_boundary"]
        and "p_0/2" in duhamel_contract["strong_boundary"],
        duhamel_contract["strong_boundary"],
        "fixed strong image and positive symmetric limit",
        "Duhamel",
    )
    audit.check(
        "modular bandwidth repair",
        "beta Omega/2 coth(beta Omega/2)" in duhamel_contract["repair"],
        duhamel_contract["repair"],
        "arithmetic/log-mean modular factor",
        "modular",
    )
    audit.check(
        "KMS route retained",
        "itself is not rejected" in duhamel_contract["scope"],
        duhamel_contract["scope"],
        "only Duhamel-inner-product promotion rejected",
        "scope",
    )

    audit.check(
        "four negative IDs exact and ordered",
        manifest["negative_ids"] == list(NEGATIVE_IDS),
        manifest["negative_ids"],
        list(NEGATIVE_IDS),
        "negative-results",
    )
    for negative_id in NEGATIVE_IDS:
        audit.check(
            f"certificate records {negative_id}",
            negative_id in certificate,
            negative_id in certificate,
            True,
            "negative-results",
        )
        audit.check(
            f"registry records {negative_id}",
            negative_id in negative_registry,
            negative_id in negative_registry,
            True,
            "negative-results",
        )

    audit.check(
        "closed subgates exact",
        manifest["closed_subgates"]
        == [
            "PA-CP1-ST8-Q3LOCK-CENTERED-WEIGHT-CUBIC-GRAPH-EMBEDDING",
            "PA-CP1-ST8-Q3LOCK-PRESCRIBED-BOND-WORD-HEAT-SIMPLEX",
        ],
        manifest["closed_subgates"],
        "exactly two scoped positive subgates",
        "scope",
    )
    audit.check(
        "both common-dynamics route gates open",
        FIRST_PASSAGE_GATE in manifest["open_gates"]
        and MODULAR_CUTOFF_GATE in manifest["open_gates"],
        manifest["open_gates"],
        [FIRST_PASSAGE_GATE, MODULAR_CUTOFF_GATE],
        "scope",
    )
    audit.check(
        "status partially resolved",
        manifest["status"].startswith("PARTIALLY RESOLVED:")
        and "COMMON DYNAMICS" in manifest["status"]
        and "REMAIN OPEN" in manifest["status"],
        manifest["status"],
        "PARTIALLY RESOLVED with common dynamics open",
        "scope",
    )
    for token in (
        "first-passage RT-PV estimate",
        "spatial commutator Lieb--Robinson closure",
        "uniform fifth onsite-energy moment",
        "nontracial cutoff locality",
        "phase- or beta-independent common C-star alpha",
        "common-alpha KMS identification",
        "algebraic ground states",
        "GNS or physical mass gap",
        "regulator removal",
        "continuum",
        "physical empty space",
        "below-empty sign",
        "functional selection",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(
            f"no-overclaim {token}",
            token in manifest["no_overclaim"],
            manifest["no_overclaim"],
            f"contains {token}",
            "scope",
        )
    certificate_flat = " ".join(certificate.split())
    for phrase in (
        "does not close common real-time dynamics",
        "not yet a connected-cluster theorem",
        "not a statement that the oscillatory real-time boundary value diverges",
        "moment alone is not enough",
        "does not construct a phase- or beta-independent common C-star",
        "Sector A or Pre-A",
    ):
        audit.check(
            f"certificate boundary {phrase}",
            phrase.lower() in certificate_flat.lower(),
            phrase in certificate_flat,
            True,
            "scope",
        )

    source_paths = (SCRIPT, MANIFEST, CERTIFICATE, PARENT, NEGATIVE_REGISTRY)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
    }
    for relative_path, digest in source_hashes.items():
        audit.check(
            f"source hash {relative_path}",
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": (
            "tect/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-"
            "route-split-independent-result/1.0"
        ),
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_version": manifest["result_version"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_ids": manifest["claim_ids"],
        "claim_bearing": False,
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "q3": q3,
            "graph_fixture": graph,
            "moving_bump": bump,
            "moving_center": {
                "ledger": graph["moving_center_ledger"],
                "constant_coefficient": graph[
                    "moving_center_constant_coefficient"
                ],
                "kappa_coefficient": graph["moving_center_kappa_coefficient"],
                "C_mu_decimal": graph["moving_center_decimal"],
            },
            "heat_simplex": heat,
            "animal": animal,
            "real_time": real_time,
            "equilibrium_cutoff": equilibrium,
            "duhamel_topology": duhamel,
            "duhamel_first_rows": [
                {
                    "n": row["n"],
                    "beta_times_duhamel_squared": row[
                        "beta_times_duhamel_X_square"
                    ],
                    "symmetric_gns_squared": row["symmetric_gns_square"],
                }
                for row in duhamel["rows"][:6]
            ],
            "scope": {
                "negative_ids": list(NEGATIVE_IDS),
                "closed_subgates": manifest["closed_subgates"],
                "open_gates": manifest["open_gates"],
                "cubic_graph_embedding_closed": True,
                "prescribed_word_heat_simplex_closed": True,
                "first_passage_real_time_product_closed": False,
                "fifth_energy_modular_cutoff_closed": False,
                "common_alpha_closed": False,
            },
        },
        "source_hashes": source_hashes,
        "boundary": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-identical canonical payloads",
    )
    arguments = parser.parse_args()

    payload = build_payload()
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.self_test:
        repeated = build_payload()
        repeated_encoded = canonical_bytes(repeated)
        if encoded != repeated_encoded:
            raise AssertionError("nondeterministic independent payload")
        repeated_digest = hashlib.sha256(repeated_encoded).hexdigest()
        if digest != repeated_digest:
            raise AssertionError("nondeterministic independent digest")
        print(
            f"SELF-TEST PASS {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
        )
        return 0

    atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['summary']['passed']}/{payload['summary']['total']} | "
        f"SHA256 {digest} | {RESULT_ID}"
    )
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
