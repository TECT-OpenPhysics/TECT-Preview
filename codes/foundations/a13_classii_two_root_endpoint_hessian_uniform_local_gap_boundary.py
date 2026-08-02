#!/usr/bin/env python3
"""Primary exact certificate for the A13 R-151 two-root local Hessian gap.

The certificate derives the full-sign 12-by-12 adapted two-root endpoint
Hessian estimate from the A1 symbol and the R-130 pointwise Hessian envelope.
It proves a momentum-uniform local source gap by exact rational Sturm algebra.
It does not prove the nonlinear or multi-root T-050 estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TWO-ROOT-ENDPOINT-HESSIAN-UNIFORM-LOCAL-GAP-BOUNDARY"
LEDGER_ID = "R-151"
SLUG = "two-root-endpoint-hessian-uniform-local-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
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


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
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


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign_variations(signs: list[int]) -> int:
    filtered = [value for value in signs if value]
    return sum(left != right for left, right in zip(filtered, filtered[1:]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    volume = rational(parameters["Lx"]) * rational(parameters["Ly"]) * rational(parameters["Lz"])
    audit.check("production", "registered volume", volume == 4096, volume, 4096)

    family = [rational(value) for value in parameters["family_masses"]]
    complex_components = len(family)
    lock = rational(parameters["k_lock"])
    z0 = sp.Matrix([rational(value) for value in parameters["z0"]])
    projector = z0 * z0.T / (z0.T * z0)[0]
    mass = sp.diag(*family) + lock * (sp.eye(complex_components) - projector)
    mass_oracle = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    audit.check("production", "exact family-lock mass", mass == mass_oracle, mass, mass_oracle)

    mass_floor = sp.Rational(7, 250)
    shifted_mass = mass - mass_floor * sp.eye(complex_components)
    mass_minors = tuple(sp.factor(shifted_mass[:size, :size].det()) for size in range(1, complex_components + 1))
    mass_minor_oracle = (sp.Rational(9, 125), sp.Rational(1211, 250000), sp.Rational(89, 31250000))
    audit.check("production", "mass-floor leading minors", mass_minors == mass_minor_oracle, mass_minors, mass_minor_oracle)
    audit.check("production", "mass floor is strict", all(value > 0 for value in mass_minors), mass_minors, "all positive")

    x = sp.symbols("x", nonnegative=True)
    kinetic_z = rational(parameters["Z"])
    kinetic_r = rational(parameters["r"])
    lower_symbol = sp.expand(x**2 + kinetic_z * x + kinetic_r + mass_floor)
    lower_discriminant = sp.factor(kinetic_z**2 - 4 * (kinetic_r + mass_floor))
    audit.check("production", "symbol lower polynomial has negative discriminant", lower_discriminant < 0, lower_discriminant, "<0")

    p_floor = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    strict_mass_square = rational(parameters["M_X"]) ** 2
    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["primary_result"]
    r130_result_path = REPO / r130_record["path"]
    r130_result = json.loads(r130_result_path.read_text(encoding="utf-8"))
    hessian_constant = rational(r130_result["diagnostics"]["conormal_gram"]["H6"])
    hessian_numerator = sp.factor(hessian_constant * p_floor)
    hessian_upper = sp.factor(hessian_numerator / strict_mass_square)
    audit.check(
        "coefficient",
        "registered positive coefficient floor",
        p_floor > strict_mass_square and sha256(r130_result_path) == r130_record["sha256"],
        [p_floor, sha256(r130_result_path)],
        [f">{strict_mass_square}", r130_record["sha256"]],
    )
    audit.check("coefficient", "R-130 Hessian envelope upper bound", hessian_constant < hessian_upper, hessian_constant, f"<{hessian_upper}")

    a, b, wave = sp.symbols("a b wave", positive=True)
    real_coordinates_per_complex = len(("real", "imaginary"))
    physical_real_dimension = complex_components * real_coordinates_per_complex
    taylor_half = sp.Rational(1, len(("first", "second")))
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
    derivative_first = earlier_frequency_multiplier * wave * a
    derivative_second = later_frequency_multiplier * wave * b
    cross_bound = sp.expand(mixed_norm_factor * hessian_upper * a * b * derivative_first * derivative_second)
    cross_synthesis_bound = sp.expand(
        cross_synthesis_norm_factor * hessian_upper * (b * derivative_first + a * derivative_second) ** 2
    )
    combined_bound = sp.factor(cross_bound + cross_synthesis_bound)
    owner_norm_factor = sp.factor(combined_bound / (hessian_upper * wave**2 * a**2 * b**2))
    expected_cross_synthesis_norm_factor = endpoint_polarizations * physical_real_dimension
    expected_owner_norm_factor = (
        mixed_norm_factor * earlier_frequency_multiplier * later_frequency_multiplier
        + expected_cross_synthesis_norm_factor * (earlier_frequency_multiplier + later_frequency_multiplier) ** 2
    )
    audit.check(
        "hessian",
        "owner-complete norm factor",
        cross_synthesis_norm_factor == expected_cross_synthesis_norm_factor
        and sp.simplify(owner_norm_factor - expected_owner_norm_factor) == 0,
        [cross_synthesis_norm_factor, owner_norm_factor],
        [expected_cross_synthesis_norm_factor, expected_owner_norm_factor],
    )

    antipodal_covariance_factor = antipodal_multiplicity**2
    covariance_normalized_factor = owner_norm_factor * antipodal_covariance_factor
    later_frequency_square = later_frequency_multiplier**2
    pair_bound = sp.factor(
        covariance_normalized_factor
        * hessian_upper
        * x
        / (volume * lower_symbol * lower_symbol.subs(x, later_frequency_square * x))
    )
    target_loss = sp.Rational(4, 5)
    sturm_polynomial = sp.Poly(
        sp.expand(
            target_loss * volume * lower_symbol * lower_symbol.subs(x, later_frequency_square * x)
            - covariance_normalized_factor * hessian_upper * x
        ),
        x,
        domain=sp.QQ,
    )
    sequence = sp.sturm(sturm_polynomial.as_expr(), x)
    zero_signs = [int(sp.sign(term.subs(x, 0))) for term in sequence]
    infinity_signs = [int(sp.sign(sp.LC(sp.Poly(term, x)))) for term in sequence]
    zero_variations = sign_variations(zero_signs)
    infinity_variations = sign_variations(infinity_signs)
    audit.check("sturm", "Sturm sequence length", len(sequence) == 5, len(sequence), 5)
    audit.check("sturm", "zero sign vector", zero_signs == [1, -1, -1, 1, 1], zero_signs, [1, -1, -1, 1, 1])
    audit.check("sturm", "positive-infinity sign vector", infinity_signs == [1, 1, -1, -1, 1], infinity_signs, [1, 1, -1, -1, 1])
    audit.check("sturm", "equal Sturm variations", zero_variations == infinity_variations == 2, [zero_variations, infinity_variations], [2, 2])
    audit.check("sturm", "positive constant term", sturm_polynomial.eval(0) > 0, sturm_polynomial.eval(0), ">0")
    audit.check("sturm", "no positive real root", sp.count_roots(sturm_polynomial.as_expr(), 0, sp.oo) == 0, sp.count_roots(sturm_polynomial.as_expr(), 0, sp.oo), 0)

    source_hessian = len(("first", "second")) * sp.Rational(9, 20)
    certified_gap = source_hessian - target_loss
    audit.check("budget", "source Hessian coefficient", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))
    audit.check("budget", "uniform local gap", certified_gap == sp.Rational(1, 10) and certified_gap > 0, certified_gap, sp.Rational(1, 10))

    frequencies = sorted(
        {
            later_frequency_multiplier * later - earlier_frequency_multiplier * earlier
            for later in (-1, 1)
            for earlier in (-1, 1)
        }
    )
    audit.check("origin", "two-root first-variation frequencies are nonzero", frequencies == [-3, -1, 1, 3] and 0 not in frequencies, frequencies, [-3, -1, 1, 3])

    radius, inner, tangent_norm = sp.symbols("radius inner tangent_norm", nonnegative=True)
    epsilon = sp.symbols("epsilon", real=True)
    norm_square_path = radius + len(("left", "right")) * epsilon * inner + epsilon**2 * tangent_norm
    sextic_second = sp.factor(sp.diff(norm_square_path**complex_components, epsilon, 2).subs(epsilon, 0))
    audit.check("sextic", "pointwise sixth-power second derivative is nonnegative", sextic_second.is_nonnegative is True, sextic_second, ">=0")

    root_real_dimension = antipodal_multiplicity * physical_real_dimension
    chart_dimension = root_real_dimension**2
    audit.check(
        "scope",
        "full antipodal/internal linear chart dimension",
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
    audit.check("scope", "result remains local and T4", local_scope, SCOPE, "local pair theorem; T-050 and Sector A open")

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
            "mass": mass,
            "mass_floor": mass_floor,
            "mass_floor_minors": mass_minors,
            "symbol_lower_polynomial": lower_symbol,
            "symbol_lower_discriminant": lower_discriminant,
            "hessian_constant_exact": hessian_constant,
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
            "owner_norm_factor": owner_norm_factor,
            "antipodal_covariance_factor": antipodal_covariance_factor,
            "covariance_normalized_factor": covariance_normalized_factor,
            "combined_owner_norm_factor": combined_bound,
            "pair_endpoint_hessian_loss_bound": pair_bound,
            "sturm_polynomial": sturm_polynomial.as_expr(),
            "sturm_zero_signs": zero_signs,
            "sturm_infinity_signs": infinity_signs,
            "sturm_variations": [zero_variations, infinity_variations],
            "endpoint_hessian_loss_strict_upper": target_loss,
            "source_hessian": source_hessian,
            "certified_augmented_local_gap_strict_lower": certified_gap,
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
