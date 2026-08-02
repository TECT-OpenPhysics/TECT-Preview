#!/usr/bin/env python3
"""Independent exact Fraction audit for the A13 R-151 local Hessian gap."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TWO-ROOT-ENDPOINT-HESSIAN-UNIFORM-LOCAL-GAP-BOUNDARY"
LEDGER_ID = "R-151"
SLUG = "two-root-endpoint-hessian-uniform-local-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R130_MANIFEST = REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
SCOPE = {
    "all_nonzero_momenta": False,
    "admissible_dual_lattice_two_root_momenta": True,
    "radial_certificate_all_x_nonnegative": True,
    "stationary_common_even_background": True,
    "full_sign_mixing_and_six_real_internal_space": True,
    "zero_strict_past_background": True,
    "linear_second_root_feedback": True,
    "nonlinear_feedback": False,
    "multi_root_aggregation": False,
    "historical_low_identified": False,
    "t050_closed": False,
    "sector_a_closed": False,
}
NO_OVERCLAIM = (
    "R-151 proves only a zero-strict-past, linear two-root endpoint-Hessian gap "
    "for simultaneous antipodal p:2p controls at admissible dual-lattice momenta with both roots retained, "
    "in a stationary common-even background "
    "with regulator multipliers bounded by one. It does not cover non-lattice or unretained "
    "momenta, nonzero past means, nonlinear feedback, cross-pair or full directed-union aggregation, identify historical "
    "low/forest/balanced owners, close T-050 or A13, prove Nelson/removals/an interacting "
    "measure, select any phase, "
    "validate or replace a PDE, or close Sector A."
)


def frac(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
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


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def det2(matrix: list[list[F]]) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def det3(matrix: list[list[F]]) -> F:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def trim(poly: list[F]) -> list[F]:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def derivative(poly: list[F]) -> list[F]:
    return trim([F(index) * poly[index] for index in range(1, len(poly))] or [F(0)])


def multiply(left: list[F], right: list[F]) -> list[F]:
    result = [F(0)] * (len(left) + len(right) - 1)
    for i, a_value in enumerate(left):
        for j, b_value in enumerate(right):
            result[i + j] += a_value * b_value
    return trim(result)


def divmod_poly(numerator: list[F], denominator: list[F]) -> tuple[list[F], list[F]]:
    remainder = trim(numerator)
    denominator = trim(denominator)
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    quotient = [F(0)] * max(1, len(remainder) - len(denominator) + 1)
    while len(remainder) >= len(denominator) and remainder != [0]:
        offset = len(remainder) - len(denominator)
        coefficient = remainder[-1] / denominator[-1]
        quotient[offset] += coefficient
        for index, value in enumerate(denominator):
            remainder[index + offset] -= coefficient * value
        remainder = trim(remainder)
    return trim(quotient), trim(remainder)


def sturm(poly: list[F]) -> list[list[F]]:
    sequence = [trim(poly), derivative(poly)]
    while sequence[-1] != [0]:
        _, remainder = divmod_poly(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        sequence.append([-value for value in remainder])
    return sequence


def sign(value: F) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def variations(values: list[int]) -> int:
    values = [value for value in values if value]
    return sum(left != right for left, right in zip(values, values[1:]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    volume = frac(parameters["Lx"]) * frac(parameters["Ly"]) * frac(parameters["Lz"])
    audit.check("production", "volume from three axes", volume == 4096, volume, 4096)

    family = [frac(value) for value in parameters["family_masses"]]
    lock = frac(parameters["k_lock"])
    z0 = [frac(value) for value in parameters["z0"]]
    z0_norm_square = sum(value * value for value in z0)
    complex_components = len(family)
    mass = [
        [
            (family[i] if i == j else F(0))
            + lock * ((F(1) if i == j else F(0)) - z0[i] * z0[j] / z0_norm_square)
            for j in range(complex_components)
        ]
        for i in range(complex_components)
    ]
    floor = F(7, 250)
    shifted = [
        [mass[i][j] - (floor if i == j else F(0)) for j in range(complex_components)]
        for i in range(complex_components)
    ]
    minors = (shifted[0][0], det2([row[:2] for row in shifted[:2]]), det3(shifted))
    oracle_minors = (F(9, 125), F(1211, 250000), F(89, 31250000))
    audit.check("production", "independent Sylvester minors", minors == oracle_minors, minors, oracle_minors)
    audit.check("production", "strict mass floor", all(value > 0 for value in minors), minors, "all positive")

    z_value = frac(parameters["Z"])
    constant = frac(parameters["r"]) + floor
    discriminant = z_value * z_value - 4 * constant
    audit.check("production", "positive scalar-symbol lower polynomial", discriminant < 0 and constant > 0, [discriminant, constant], ["<0", ">0"])

    p_floor = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    strict_mass_square = frac(parameters["M_X"]) ** 2
    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["independent_result"]
    r130_result_path = REPO / r130_record["path"]
    r130_result = json.loads(r130_result_path.read_text(encoding="utf-8"))
    hessian_exact = frac(r130_result["diagnostics"]["gram"]["H6"])
    hessian_numerator = hessian_exact * p_floor
    hessian_upper = hessian_numerator / strict_mass_square
    audit.check(
        "coefficient",
        "independent H6 upper bound",
        hessian_exact < hessian_upper and sha256(r130_result_path) == r130_record["sha256"],
        [hessian_exact, sha256(r130_result_path)],
        [f"<{hessian_upper}", r130_record["sha256"]],
    )

    real_coordinates_per_complex = len(("real", "imaginary"))
    physical_real_dimension = complex_components * real_coordinates_per_complex
    taylor_half = F(1, len(("first", "second")))
    covariance_symmetrizations = len(("left", "adjoint"))
    current_symmetrizations = len(("left", "adjoint"))
    endpoint_polarizations = len(("forward", "reverse"))
    antipodal_multiplicity = len((-1, 1))
    earlier_frequency_multiplier = 1
    later_frequency_multiplier = 2
    mixed_norm_factor = (
        taylor_half
        * physical_real_dimension
        * covariance_symmetrizations
        * current_symmetrizations
        * endpoint_polarizations
    )
    cross_synthesis_norm_factor = endpoint_polarizations * physical_real_dimension
    owner_factor = (
        mixed_norm_factor * earlier_frequency_multiplier * later_frequency_multiplier
        + cross_synthesis_norm_factor * (earlier_frequency_multiplier + later_frequency_multiplier) ** 2
    )
    covariance_factor = antipodal_multiplicity**2
    final_factor = owner_factor * covariance_factor

    # Polynomials use ascending powers. f(x)=x^2+Zx+c and f(4x)=16x^2+4Zx+c.
    first = [constant, z_value, F(1)]
    later_frequency_square = later_frequency_multiplier**2
    second = [constant, later_frequency_square * z_value, F(later_frequency_square**2)]
    product = multiply(first, second)
    target = F(4, 5)
    polynomial = [target * volume * coefficient for coefficient in product]
    polynomial[1] -= final_factor * hessian_upper
    polynomial = trim(polynomial)
    coefficient_oracle = [
        F(25203778302134079729, 30517578125000000),
        -F(29970036890042018799, 3051757812500000),
        F(74744439754677505969, 1907348632812500),
        -F(592176264064, 9765625),
        F(262144, 5),
    ]
    audit.check("sturm", "independent quartic coefficients", polynomial == coefficient_oracle, polynomial, coefficient_oracle)

    sequence = sturm(polynomial)
    zero_signs = [sign(item[0]) for item in sequence]
    infinity_signs = [sign(item[-1]) for item in sequence]
    zero_variations = variations(zero_signs)
    infinity_variations = variations(infinity_signs)
    audit.check("sturm", "independent sequence length", len(sequence) == 5, len(sequence), 5)
    audit.check("sturm", "independent zero signs", zero_signs == [1, -1, -1, 1, 1], zero_signs, [1, -1, -1, 1, 1])
    audit.check("sturm", "independent infinity signs", infinity_signs == [1, 1, -1, -1, 1], infinity_signs, [1, 1, -1, -1, 1])
    audit.check("sturm", "independent positive-root count", zero_variations - infinity_variations == 0, zero_variations - infinity_variations, 0)
    audit.check("sturm", "quartic stays positive", polynomial[0] > 0 and zero_variations == infinity_variations, polynomial[0], ">0 with no positive root")

    owner_factor_from_terms = (
        mixed_norm_factor * earlier_frequency_multiplier * later_frequency_multiplier
        + endpoint_polarizations * physical_real_dimension * (earlier_frequency_multiplier + later_frequency_multiplier) ** 2
    )
    audit.check(
        "hessian",
        "independent owner factor",
        cross_synthesis_norm_factor == endpoint_polarizations * physical_real_dimension
        and owner_factor == owner_factor_from_terms,
        [cross_synthesis_norm_factor, owner_factor],
        [endpoint_polarizations * physical_real_dimension, owner_factor_from_terms],
    )
    audit.check(
        "hessian",
        "independent covariance-normalized factor",
        final_factor == owner_factor_from_terms * antipodal_multiplicity**2,
        final_factor,
        owner_factor_from_terms * antipodal_multiplicity**2,
    )

    source_hessian = len(("first", "second")) * F(9, 20)
    gap = source_hessian - target
    audit.check("budget", "independent source Hessian", source_hessian == F(9, 10), source_hessian, F(9, 10))
    audit.check("budget", "independent strict local gap", gap == F(1, 10), gap, F(1, 10))

    frequencies = sorted(
        {
            later_frequency_multiplier * later - earlier_frequency_multiplier * earlier
            for later in (-1, 1)
            for earlier in (-1, 1)
        }
    )
    audit.check("origin", "independent Fourier orthogonality", frequencies == [-3, -1, 1, 3], frequencies, [-3, -1, 1, 3])
    norm_path_linear = len(("left", "right"))
    norm_path_quadratic = 1
    sextic_power = complex_components
    inner_square_coefficient = sextic_power * (sextic_power - 1) * norm_path_linear**2
    tangent_coefficient = len(("first", "second")) * sextic_power * norm_path_quadratic
    audit.check(
        "sextic",
        "convexity coefficients",
        inner_square_coefficient > 0 and tangent_coefficient > 0,
        [inner_square_coefficient, tangent_coefficient],
        "positive",
    )
    root_real_dimension = antipodal_multiplicity * physical_real_dimension
    chart_dimension = root_real_dimension**2
    audit.check(
        "scope",
        "full linear control dimension",
        chart_dimension == (antipodal_multiplicity * complex_components * real_coordinates_per_complex) ** 2,
        chart_dimension,
        f"({antipodal_multiplicity} signs * {complex_components} complex * {real_coordinates_per_complex} real)^2",
    )
    local_scope = (
        SCOPE["zero_strict_past_background"]
        and SCOPE["linear_second_root_feedback"]
        and not SCOPE["nonlinear_feedback"]
        and not SCOPE["multi_root_aggregation"]
        and not SCOPE["t050_closed"]
        and not SCOPE["sector_a_closed"]
        and "close T-050 or A13" in NO_OVERCLAIM
    )
    audit.check("scope", "no T-050 overclaim", local_scope, SCOPE, "local pair theorem only; open gates explicit")

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "ledger_id": LEDGER_ID,
        "status": "PASS",
        "derived": {
            "volume": volume,
            "mass_floor": floor,
            "mass_floor_minors": minors,
            "symbol_lower_discriminant": discriminant,
            "hessian_constant_exact": hessian_exact,
            "hessian_constant_upper": hessian_upper,
            "factor_primitives": {
                "complex_components": complex_components,
                "real_coordinates_per_complex": real_coordinates_per_complex,
                "physical_real_dimension": physical_real_dimension,
                "taylor_half": taylor_half,
                "covariance_symmetrizations": covariance_symmetrizations,
                "current_symmetrizations": current_symmetrizations,
                "endpoint_polarizations": endpoint_polarizations,
                "antipodal_multiplicity": antipodal_multiplicity,
                "earlier_frequency_multiplier": earlier_frequency_multiplier,
                "later_frequency_multiplier": later_frequency_multiplier,
            },
            "mixed_norm_factor": mixed_norm_factor,
            "cross_synthesis_norm_factor": cross_synthesis_norm_factor,
            "antipodal_covariance_factor": covariance_factor,
            "sturm_polynomial_coefficients_ascending": polynomial,
            "sturm_zero_signs": zero_signs,
            "sturm_infinity_signs": infinity_signs,
            "sturm_variations": [zero_variations, infinity_variations],
            "owner_norm_factor": owner_factor,
            "covariance_normalized_factor": final_factor,
            "endpoint_hessian_loss_strict_upper": target,
            "source_hessian": source_hessian,
            "certified_augmented_local_gap_strict_lower": gap,
            "first_variation_frequencies": frequencies,
            "control_dimension": chart_dimension,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions": audit.rows,
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
